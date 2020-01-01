import asyncio
import uuid
import os
import shutil
from utils.logger import get_logger

logger = get_logger(__name__)

def logging_function(func):
    async def get_arguments(*args, **kwargs):
        logger.info(f'{func.__name__}: args={args}, kwargs={kwargs}')
        return await func(*args, **kwargs)
    return get_arguments

class FfmpegError(Exception):
    pass

class VideoProcessing:
    def __init__(self, audio_filename: str, video_file_path: str, cache: str):
        self._filename = audio_filename
        self.video_file_path = video_file_path
        self.cache_path = self._create_cache(cache)
        self.files = []

    @staticmethod
    def _create_cache(cache_dir_name: str):
        filename = uuid.uuid4().hex
        os.mkdir(cache_dir_name + '/' + filename)
        return cache_dir_name + '/' + filename

    @staticmethod
    def _is_file_exist(filename):
        return os.path.isfile(filename)

    def _get_full_path(self, filename: str) -> str:
        return os.getcwd() + '/' + self.cache_path + '/' + filename

    @staticmethod
    @logging_function
    async def _async_shell_command(program, *args):
        process = await asyncio.create_subprocess_exec(program, *args, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if stdout:
            logger.info(stdout.decode().strip())
        if stderr:
            logger.info(stderr.decode().strip())
        
    async def _cut_audio(self, offset: float, run_time: float, args: str or None = None) -> str:
        audio_filename = self._get_full_path(uuid.uuid4().hex + '.mp3')
        if args:
            await self._async_shell_command(
                'ffmpeg', 
                '-y', 
                '-ss', f'00:00:{offset:0>4.1f}', 
                '-t', f'00:00:{run_time:0>4.1f}', 
                '-i', self._filename, 
                '-acodec', 'libmp3lame',
                '-af', args,
                audio_filename
            )
        else:
            await self._async_shell_command(
                'ffmpeg', 
                '-y', 
                '-ss', f'00:00:{offset:0>4.1f}', 
                '-t', f'00:00:{run_time:0>4.1f}', 
                '-i', self._filename, 
                '-acodec', 'libmp3lame',
                audio_filename
            )
        if not self._is_file_exist(audio_filename):
            raise FfmpegError('File not exist: ' + audio_filename)
        return audio_filename

    async def _concat_audio(self, audio_filenames: list, silences_filenames: list) -> str:
        audio_filename = self._get_full_path(uuid.uuid4().hex + '.mp3')
        concat_pipline = []
        for silence, audio in zip(silences_filenames, audio_filenames):
            concat_pipline.extend([silence, audio])
        str_pipline = '|'.join(concat_pipline)
        await self._async_shell_command(
            'ffmpeg','-y' ,'-i', f'concat:{str_pipline}', '-acodec', 'libmp3lame', audio_filename
        )
        if not self._is_file_exist(audio_filename):
            raise FfmpegError('File not exist: ' + audio_filename)
        return audio_filename
    
    async def _generate_video(self, audio_filename: str) -> str:
        filename = self._get_full_path(uuid.uuid4().hex + '.mp4')
        await self._async_shell_command(
            'ffmpeg',
            '-y', 
            '-i', self.video_file_path,
            '-i', audio_filename,
            '-c:v', 'copy',
            '-filter_complex', '[0:a]aformat=fltp:44100:stereo,apad[0a];[1]aformat=fltp:44100:stereo,volume=0.7[1a];[0a][1a]amerge[a]',
            '-map', '0:v',
            '-map','[a]',
            filename
        )
        if not self._is_file_exist(filename):
            raise FfmpegError('File not exist: ' + filename)
        return filename

    def pipeline(self) -> str:
        raise NotImplementedError()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        shutil.rmtree(self.cache_path)


class YodaVideoProcessing(VideoProcessing):
    video_file_path = 'files/video/yoda.mp4'
    cache = 'files/cache'
    silince_filenames = ('files/audio/silence/silence6.mp3','files/audio/silence/silence4_5.mp3', 'files/audio/silence/silence3.mp3')

    def __init__(self, audio_filename):
        super().__init__(audio_filename, self.video_file_path, self.cache)

    async def pipeline(self) -> str:
        music1 = await self._cut_audio(0, 4.5)
        music2 = await self._cut_audio(4.5, 4.5)
        music3 = await self._cut_audio(9.0, 2.0, args="firequalizer=gain_entry='entry(0,30);entry(250,40)")
        music_concat = await self._concat_audio([music1, music2, music3], [self.silince_filenames[0], self.silince_filenames[1], self.silince_filenames[0], self.silince_filenames[2]])
        return await self._generate_video(music_concat)


async def main():
    yvp = YodaVideoProcessing('files/audio/user/music.mp3')
    print(await yvp.pipeline())


if __name__ == "__main__":
    asyncio.run(main())