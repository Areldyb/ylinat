# Your Laptop Is Now A Typewriter (YLINAT)

YLINAT is a text "editor" that does not allow you to edit your text. You can write, but you cannot backspace or reposition the cursor.

Created for [Timasomo 2023](https://tildes.net/~creative.timasomo/1bvk/timasomo_2023_the_showcase)

## Features

* Simple, boring UI with minimal distractions
* Autosave
* Word count, both in total and for the current session
* Font, margin, and line length options, so you can make it _your_ typewriter
* A completely useless "Edit" menu
* "Goldfish mode" for when you can't stand to look at what you wrote before
* A text box that won't let you fix that typo no matter how much you cry, scream, or beg

## Getting set up

If you're familiar with Python, `pip install -r requirements.txt` should get you what you need but you already knew that.

> On Linux, I found that I also needed to install the libxcb-cursor0 library. YMMV.

If you're pretty sure a python is a kind of snake, don't worry: there are ready-to-run binaries for Windows and Mac available as well.

> Well, _almost_ ready to run: modern operating systems are skeptical of new programs from unknown developers.
> * On Windows, SmartScreen is likely to complain the first time you run it, and you'll need to give it permission to run.
> * On Mac, you'll probably be prevented from running the app until you control-click on it, then click "Open". It should work normally after that.
> 
> If any of that sketches you out too much, good. My day job is in infosec; please don't make a habit of creating security exceptions for random bits of code you downloaded from the internet.

## Why would anyone want this?

I'm hoping it might help people who have trouble silencing their inner critic and just need to bash out that first draft, but mostly I wrote it for fun. I imagine it will be very frustrating to use.

## How do I edit what I've written?

You don't.

## No, I mean I've finished my draft, now how do I edit it?

Oh! Congrats!

Take your file and open it in your full-featured text editor or word processor of choice. You no longer need your laptop to be a typewriter.

## Contributing

If it's still 2023 and you've found a bug, go ahead and open an issue for it. In particular, if you've found a way to edit text in this program that isn't convoluted and weird (meaning, someone might stumble on it by accident), I'd really like to fix that.

Otherwise, I don't plan on doing much more with this, so if you want to make it better, please fork it!

## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
