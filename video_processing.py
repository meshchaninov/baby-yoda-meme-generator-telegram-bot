import asyncio
import uuid
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def logging_function(func):
    async def get_arguments(*args, **kwargs):
        logger.info(f'func_name={func.__name__}, args={args}, kwargs={kwargs}')
        return await func(*args, **kwargs)
    return get_arguments

class FfmpegError(Exception):
    pass

class VideoProcessing:
    def __init__(self, audio_filename: str, video_file_path: str, cache: str):
        self._filename = audio_filename
        self.video_file_path = video_file_path
        self.cache = cache
        self.cache_path = cache

    @logging_function
    def _create_cache(self):
        filename = uuid.uuid4().hex
        os.mkdir(self.cache + '/' + filename)
        self.cache_path = self.cache + '/' + filename


    def _get_full_path(self, filename: str) -> str:
        return os.getcwd() + '/' + self.cache_path + '/' + filename

    @staticmethod
    async def _async_shell_command(program, *args):
        new_args = []
        for elem in args:
            new_args.extend(elem.split(' '))
        process = await asyncio.create_subprocess_exec(program, *new_args, stdout=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        # Return stdout
        if stdout.decode().strip():
            raise FfmpegError()
        
    @logging_function
    async def _cut_audio(self, offset: float, run_time: float, args: str or None = None) -> str:
        audio_filename = self._get_full_path(uuid.uuid4().hex + '.mp3')
        if args:
            await self._async_shell_command(
                'ffmpeg', 
                '-y', 
                f'-ss 00:00:{offset:0>4.1f}', 
                f'-t 00:00:{run_time:0>4.1f}', 
                f'-i {self._filename}', 
                '-acodec copy',
                f'-af {args}'
                f'{audio_filename}'
            )
        else:
            await self._async_shell_command(
                'ffmpeg', 
                '-y', 
                f'-ss 00:00:{offset:0>4.1f}', 
                f'-t 00:00:{run_time:0>4.1f}', 
                f'-i {self._filename}', 
                '-acodec copy',
                f'{audio_filename}'
            )

        return audio_filename

    @logging_function
    async def _concat_audio(self, audio_filenames: list, silences_filenames: list) -> str:
        audio_filename = self._get_full_path(uuid.uuid4().hex + '.mp3')
        concat_pipline = []
        for silence, audio in zip(silences_filenames, audio_filenames):
            concat_pipline.extend([silence, audio])
        str_pipline = '|'.join(concat_pipline)
        await self._async_shell_command(
            'ffmpeg','-y' ,'-i', f'concat:{str_pipline}', '-acodec copy', f'{audio_filename}'
        )
        return audio_filename
    
    @logging_function
    async def _generate_video(self, audio_filename: str) -> str:
        filename = self._get_full_path(uuid.uuid4().hex + '.mp4')
        await self._async_shell_command(
            'ffmpeg',
            '-y', 
            f'-i {self.video_file_path}',
            f'-i {audio_filename}',
            '-c:v copy',
            '-filter_complex', '[0:a]aformat=fltp:44100:stereo,apad[0a];[1]aformat=fltp:44100:stereo,volume=0.7[1a];[0a][1a]amerge[a]',
            '-map 0:v',
            '-map','[a]',
            f'{filename}'
        )
        return filename

    def pipeline(self) -> str:
        raise NotImplementedError()

    @logging_function
    async def __aenter__(self):
        return await self.pipeline()

    @logging_function
    async def __aexit__(self, exc_type, exc, tb):
        os.remove(self.cache_path)


class YodaVideoProcessing(VideoProcessing):
    video_file_path = 'files/video/yoda.mp4'
    cache = 'files/cache'
    silince_filenames = ('files/audio/silence/silence6.mp3','files/audio/silence/silence4_5.mp3', 'files/audio/silence/silence3.mp3')

    def __init__(self, audio_filename):
        super().__init__(audio_filename, self.video_file_path, self.cache)

    @logging_function
    async def pipeline(self) -> str:
        music1 = await self._cut_audio(0, 4.5)
        music2 = await self._cut_audio(4.5, 4.5)
        music3 = await self._cut_audio(9.0, 2.0)
        music_concat = await self._concat_audio([music1, music2, music3], [self.silince_filenames[0], self.silince_filenames[1], self.silince_filenames[0], self.silince_filenames[2]])
        return await self._generate_video(music_concat)


async def main():
    async with YodaVideoProcessing('files/audio/user/music.mp3') as yvp:
        print(await yvp.pipeline())


if __name__ == "__main__":
    asyncio.run(main())