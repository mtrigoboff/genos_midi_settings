# Print Genos MIDI Settings
*by [Michael Trigoboff](http://spot.pcc.edu/~mtrigobo/personal/music.html)*  
(*version 1.0*)

## The Problem

The Genos allows you to have up to 10 user-edited MIDI "templates", each of which specifies MIDI settings for the Genos. You can view and edit these settings on the Genos touchscreen.

Since you can have only 10 user templates at a time, it's important to make sure you don't have templates that are essentially duplicates of each other. The template viewer is split up into a lot of separate pages, and this can make it extremely difficult to compare two of these MIDI templates and tell how different they may or may not be.

# A Solution

The Genos allows you to save a set of up to 10 MIDI templates in a **.msu** file. You can do it on the Utility page described on p. 159 of the Genos Refernce Manual:

(*There is an image of that page below. I have noticed that, occasionally, images included in this Jupyter notebook may not appear. Hopefully in that case the text is explicit enough to enable your successful use of the notebook.*)

![Genos utility Setup Files backup page](https://drive.google.com/uc?export=view&id=1Q_G-ITNfeIFzA8mgwGFJOlC29V4lahQs)

It occurred to me that I could write code to read in a **.msu** file, and print out each of its MIDI templates as a text file. This would allow someone to look at all of the settings at once for each of the templates, which would make it much easier to compare templates with each other.

You can also use a diff utility like [WinMerge](https://winmerge.org/), which can show you two text files side-by-side and hilite the differences between them.

I did it as a [Jupyter Notebook](https://en.wikipedia.org/wiki/Project_Jupyter), which is a very user-friendly way to combine code with the instructions for its use. (This is an example of [literate programming](https://en.wikipedia.org/wiki/Literate_programming), an idea invented quite a few decades ago by Stanford computer science professor [Donald Knuth](https://en.wikipedia.org/wiki/Donald_Knuth).)
