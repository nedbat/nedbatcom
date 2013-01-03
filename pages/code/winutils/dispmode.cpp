// DispMode.cpp: Set or show the current display mode.
// Copyright 2002-2003, Ned Batchelder, http://www.nedbatchelder.com

#include <stdio.h>
#include <tchar.h>
#include <windows.h>

void
PrintDevMode(DEVMODE & devmode)
{
    printf("%d x %d x %d (%d Hz)\n", 
        devmode.dmPelsWidth, 
        devmode.dmPelsHeight, 
        devmode.dmBitsPerPel,
        devmode.dmDisplayFrequency
        );
}

void
ListSettings()
{
    DEVMODE devmode;
    int     iModeNum;

    for (iModeNum = 0; ; iModeNum++) {
        if (::EnumDisplaySettings(NULL, iModeNum, &devmode)) {
            PrintDevMode(devmode);
        }
        else {
            break;
        }
    }
}

void
ShowSettings()
{
    DEVMODE curDevmode;

    ::EnumDisplaySettings(NULL, ENUM_CURRENT_SETTINGS, &curDevmode);
    PrintDevMode(curDevmode);
}

void
ChangeSettings(int width, int depth, int freq, DWORD flags)
{
    DEVMODE curDevmode;
    DEVMODE devmode;
    int     iModeNum;

    ::EnumDisplaySettings(NULL, ENUM_CURRENT_SETTINGS, &curDevmode);

    if (width == 0) {
        width = curDevmode.dmPelsWidth;
    }
    if (depth == 0) {
        depth = curDevmode.dmBitsPerPel;
    }
    if (freq == 0) {
        freq = curDevmode.dmDisplayFrequency;
    }

    for (iModeNum = 0; ; iModeNum++) {
        if (::EnumDisplaySettings(NULL, iModeNum, &devmode)) {
            // See if this setting has the right width.
            if (devmode.dmPelsWidth != width) {
                continue;
            }

            // See if this setting has the right depth.
            if (devmode.dmBitsPerPel != depth) {
                continue;
            }

            // See if this setting has the right frequency.
            if (devmode.dmDisplayFrequency != freq) {
                continue;
            }

            // This new setting satisfies all the criteria. Try it.
            devmode.dmFields |= DM_PELSWIDTH | DM_PELSHEIGHT | DM_BITSPERPEL | DM_DISPLAYFREQUENCY;
            LONG res = ::ChangeDisplaySettings(&devmode, CDS_TEST);

            switch (res) {
            case DISP_CHANGE_SUCCESSFUL:
                res = ::ChangeDisplaySettings(&devmode, flags);
                switch (res) {
                case DISP_CHANGE_SUCCESSFUL:
                    return;

                case DISP_CHANGE_NOTUPDATED:
                    printf("Settings changed, but not permanently.\n");
                    return;

                default:
                    printf("Something odd happened.\n");
                    break;
                }
                break;

            case DISP_CHANGE_RESTART:
                printf("The computer needs to be restarted to switch to these settings\n");
                break;

            default:
                printf("Something odd happened.\n");
                break;
            }
        }
        else {
            break;
        }
    }

    printf("Couldn't change settings.\n");
}

void
Usage()
{
    printf(
        "DISPMODE - Set or show the current display settings.\n"
        "Copyright (c) 2002-2003, Ned Batchelder, http://www.nedbatchelder.com\n"
        "Options:\n"
        "  -l            List the possible settings.\n"
        "  -c            Show the current settings.\n"
        "  -p            Make the settings permanent (used next time).\n"
        "  width         Set the display to the given width (width > 300)\n"
        "  depth         Set the display to the given depth (depth < 300)\n"
        "  freq          Set the display to the given refresh rate (freq like '##Hz')\n"
        );
}

int 
_tmain(int argc, _TCHAR* argv[])
{
    int width = 0;
    int depth = 0;
    int freq = 0;
    DWORD flags = 0;

    argc--, argv++;
    while (argc > 0) {
        if (argv[0][0] == '-' || argv[0][0] == '/') {
            switch (tolower(argv[0][1])) {
            case 'c':
                ShowSettings();
                return 0;

            case 'h': case 'v': case '?':
                Usage();
                return 0;

            case 'l':
                ListSettings();
                return 0;
            
            case 'p':
                flags |= CDS_UPDATEREGISTRY;
                break;

            default:
                printf("Don't know option %s\n", argv[0]);
                Usage();
                return 1;
            }
        }
        else {
            // It's an argument.
            int n = atoi(argv[0]);
            
            if (argv[0][strlen(argv[0])-1] == 'z') {
                if (freq == 0) {
                    freq = n;
                }
                else {
                    printf("Only specify one frequency\n");
                    return 1;
                }
            }
            else if (n < 300) {
                if (depth == 0) {
                    depth = n;
                }
                else {
                    printf("Only specify one depth\n");
                    return 1;
                }
            }
            else {
                if (width == 0) {
                    width = n;
                }
                else {
                    printf("Only specify one width\n");
                    return 1;
                }
            }
        }

        argc--, argv++;
    }

    // Now do something.

    if (width > 0 || depth > 0 || freq > 0) {
        ChangeSettings(width, depth, freq, flags);
    }
    else {
        Usage();
    }

    return 0;
}
