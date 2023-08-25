from . import options, consts
from .os_tools import get_os

current_os = get_os()
if current_os == consts.OS_WINDOWS:
    from cytolk import tolk

    tolk.try_sapi(True)
    tolk.load("__compiled__" not in globals())

elif current_os == consts.OS_MAC:
    from . import NSSS

    speaker = NSSS.NSSS()

elif current_os == consts.OS_LINUX:
    import speechd

    linux_speaker = speechd.Speaker("Loading...")


def speak(text, interupt=True, *args, **kwargs):
    if current_os == consts.OS_WINDOWS:
        tolk.speak(text, interupt)

    elif current_os == consts.OS_LINUX:
        if interupt:
            linux_speaker.cancel()
        linux_speaker.speak(text)

    elif current_os == consts.OS_MAC:
        speaker.set("rate", 600)
        speaker.speak(text, interupt)
