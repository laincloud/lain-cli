# -*- coding: utf-8 -*-
def version():
    """
    Semantic Version x.x.x
    """

    import lain_sdk
    import lain_cli
    print("lain sdk version: {}".format(lain_sdk.__version__))
    print("lain cli version: {}".format(lain_cli.__version__))
