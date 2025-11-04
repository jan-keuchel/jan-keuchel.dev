---
title: Writing a shortcut helper
desc: This post shows my approach and steps to writing a shortcut helper in bash for hyprland using rofi.
published: 21.09.2025
---


## What is a shortcut helper?
A shortcut helper is an interface enabling you to search for the actions you wish to perform or problems you wish to resolve.
It provides you with the shortcut you were looking for and the option of executing the specific command right away.

## Why bother creating a shortcut helper?
If you're using a tiling window manager, you've probably configured a system that is tailored to your needs and solves sparcely encountered but tedious to resolve issues easily.
This involves having some highly customized shortcuts for seldom encountered situations.
Depending on how frequently you come across said situations, and, hence, use configured shortcuts, they can easily be forgotten.
This leaves you opening your configuration and searching for the shortcut in your editor, waisting precisely the time you wanted to save when you sat down and configured the shortcut in the first place.

## What was the aim for this specific shortcut helper?
I wanted to devise a simple looking and searchable shortcut helper using bash and rofi.
A few questions arose: I don't want to display every single shortcut defined in the configureation file, so, do I create an additional file with all the shortcuts I want to search through or do I somehow filter out specified shortcuts?
How do I add searchable tags and descriptions to the respective shortcuts?
How do I display the list of shortcuts and descriptions in a table-like manner?
What precisely do I want to display in the rofi selection menu?
And finally: upon selection, how do I execute the command?

## Here are my answers to above questions:
To avoid inconsistency issues due to multiple files, the shortcuts and corresponding descriptions will be extracted from the configuration file.
In order to filter out only specific shortcuts, the corresponding lines need to be altered in some way (e.g. the declaration of the bindings will be modified from `bind = [...]` to `bind= [...]` - No space in front of the equal sign).
To easily pair up shortcuts and their descriptions, each line - and therefore shortcut - ends with a comment, that being, the shortcut's description.
Finally, what should be displayed in the rofi selection menu are the shortcuts on the left hand side, and, formatted nicely in a column, the descriptions on the right hand side.

## Needed CLI tools

The script is written in bash, as it is available on virtually every system and hence won't lead to any dependency issues.
I was aware of a few command line tools such as `grep`, `sed` and `awk` but haven't used the latter two in quite some time.
After doing some reading on these tools - and writing the script - here is what's necessary in order to understand it - and potentially write your own version:

- `grep` allows you to filter text input based on a provided pattern.
It can thus be used to easily select the desired lines of shortcut definitions from the configuration file, because said lines have been transformed previously.

- `sed` will be used to do simple search-and-replace operations.
The syntax is quite simple: `sed 's/search-term/replacement/[options]'`.
By default, `sed` replaces the first occurence of the search-term in each line line with the provided replacement.
The only option needed in this script is the `g` option which allows you to change this default behaviour so that every single occurence of the serch-term will be replaced.

- `awk` splits every line into tokens based on some delimiter, creating, in essence, columns.
Of those, some can be selected as the new output.
To give an example: `awk -F ':' '{print $1 $3 $4}'` splits every line colon-wise and produces an output of columns 1, 3 and 4 (not zero-based) separated by spaces.

- Another tool used was `column`.
This, I had not heard of before.
In short, it takes some text input and formats it into a table-like output.

## The Format of configuration files

I use Hyprland.
Consequently my keybindings may be defined in a different way than in your case.
As long as you have access to a human readable text file, this post is of use to you as you can simple adjust the script in accordance with your syntax.
To better visualize and demonstrate what is happening along the way, I'm going to use part of my config file, as well as command output based on that snippet.
The snippet used for demonstation purposes only is this:

{% highlight conf linenos %}
{% include 2025-09-21-writing-a-shortcut-helper/snippet-00 %}
{% endhighlight %}

{% comment %}{: .highlight-block .highlight-note}{% endcomment %}
(I have deliberately messed up the indentation to demonstrate different issues that need to be addressed regarding whitespace)

To elaborate, each line represents a shortcut specified as a four-tupel.
The first item are so called mod-keys such as ALT, WIN, CTRL.
Second are normal keys.
Third are the dispatchers.
Think of them as different commands you can execute (You could execute a command line argument, move some window to a workpace or send a signal to a specific window).
Fourth are the arguments provided to the dispatcher.
The words that have a dollar sign preceeding them are variables.

Actually, I have another file just for the programs I use so that I can easily swap them out in one location.
Here's part of that file:

{% highlight config linenos %}
{% include 2025-09-21-writing-a-shortcut-helper/snippet-01 %}
{% endhighlight %}

## Breaking down the script.

First, store the file with the shortcut definitions in a variable
{% highlight bash linenos %}
KEYBINDINGS_FILE="$HOME/.config/hypr/hyprland_keybindings.conf"
{% endhighlight %}

. The next step is to extricate the definitions of those shortcuts we want displayed in the helper and bring them into a homogenous layout.
Because of preceding adjustments every definition we want displayed has the prefix `bind= `.
Thus, we can reduce the entire configuration file down to solely the desired lines by grepping for this string: 

- Command:
{% highlight bash linenos %}
grep "bind= " "$KEYBINDINGS_FILE"
{% endhighlight %}
- Output:
{% highlight bash linenos %}
{% include 2025-09-21-writing-a-shortcut-helper/snippet-02 %}
{% endhighlight %}

At this point, the amount of spaces or tabs between words may vary.
Consequently, the next step is to standardize the lines.
We are first going to reduce whitespace down to a single space 

- Command:
{% highlight bash linenos %}
grep "bind= " bindings.conf | \
    sed -E  -e 's/[[:space:]]+/ /g' \
{% endhighlight %}
- Output:
{% highlight bash linenos %}
{% include 2025-09-21-writing-a-shortcut-helper/snippet-03 %}
{% endhighlight %}

{: .highlight-block .highlight-hint}
`-E` simply enables extended regular espressions, such that the expression `[[:space:]]` can be used to search for every occurence of whitespace (spaces, tabs, etc.). 
Furthermore, multiple search-and-replace operations will be executed. Every single pattern is denoted by the preceeding `-e` flag.

, then remove the `bind= ` prefix along with preceeding spaces from each line 
- Command:
{% highlight bash linenos %}
grep "bind= " bindings.conf | \
    sed -E  -e 's/[[:space:]]+/ /g' \
            -e 's/ *bind= *//' \
{% endhighlight %}
- Output:
{% highlight bash linenos %}
{% include 2025-09-21-writing-a-shortcut-helper/snippet-04 %}
{% endhighlight %}

and subsequently remove every not needed space - such as after a comma 

- Command:
{% highlight bash linenos %}
grep "bind= " bindings.conf | \
    sed -E  -e 's/[[:space:]]+/ /g' \
            -e 's/ *bind= *//' \
            -e 's/, /,/g' \
{% endhighlight %}
- Output:
{% highlight bash linenos %}
{% include 2025-09-21-writing-a-shortcut-helper/snippet-05 %}
{% endhighlight %}

or around the hash (#) at the starting point of the comment 

- Command:
{% highlight bash linenos %}
grep "bind= " bindings.conf | \
    sed -E  -e 's/[[:space:]]+/ /g' \
            -e 's/ *bind= *//' \
            -e 's/, /,/g' \
            -e 's/ *# */,/g'
{% endhighlight %}
- Output:
{% highlight bash linenos %}
{% include 2025-09-21-writing-a-shortcut-helper/snippet-06 %}
{% endhighlight %}

.
The result is that every lines words are separated either by a singular space or comma.
This shortcut list will make further string manipulation manageable.
Then, using `awk`, shortcuts and descriptions will be filtered out 

- Command:
{% highlight bash linenos %}
echo "$SHORTCUT_LIST" | awk -F ',' '{print $1" "$2"@:"$NF}'
{% endhighlight %}
- Output:
{% highlight bash linenos %}
{% include 2025-09-21-writing-a-shortcut-helper/snippet-07 %}
{% endhighlight %}

{: .highlight-block .highlight-hint}
The `$NF` simply means "the last column". `@` is simply used as another delimiter - it could be replaced by any other character.

, formatted using `column` 

- Command:
{% highlight bash linenos %}
echo "$SHORTCUT_LIST" | awk -F ',' '{print $1" "$2"@:"$NF}' | column -s '@' -t
{% endhighlight %}
- Output:
{% highlight bash linenos %}
{% include 2025-09-21-writing-a-shortcut-helper/snippet-08 %}
{% endhighlight %}

{: .highlight-block .highlight-hint}
`-s`: seperator, `-t` table output.

and thereupon displayed to the user - you - using rofi 
- Command:
{% highlight bash linenos %}
SELECTED=$(echo "$TABLE" | rofi -i -dmenu -p "")
{% endhighlight %}
- Rofi output:
![Rofi showing the formatted shortcut table](/assets/images/shortcut_helper_display_of_content.png)

From this selection the description and trailing whitespace can immediately be removed as it is no longer needed 
- Command:
{% highlight bash linenos %}
echo "$SELECTED" | awk -F ':' '{print $1}' | sed 's/ *$//'
{% endhighlight %}
- Output:
{% highlight bash linenos %}
$mod Return
{% endhighlight %}

. Now that we have the selection, we actually can't execute the corresponding command as all we have is the shortcut, not the command.
We now need to extract the command from our shortcut list by grepping for the selected shortcut in the bindings list and thereafter selecting specific columns from that line using `awk` 
{% highlight bash linenos %}
echo "$SHORTCUT_LIST" | sed 's/,/ /' | grep "$SELECTED" | awk -F ',' '{print $2" "$3}'
{% endhighlight %}

{: .highlight-block .highlight-hint}
The search-and-replace executed with `sed` replaces the first occurence of a comma with a space.
This is done because we removed the comma before displaying the shorcut list in rofi - for aesthetic purposes.
We can't grep for it unless we do the same alteration here again.

And finally, the command can be executed.
{% highlight bash linenos %}
if [[ $COMMAND == exec* ]]; then
    eval "$COMMAND"
else
    hyprctl dispatch "$COMMAND"
fi
{% endhighlight %}

## What went wrong?

Somehow, multiple commands couldn't be executed.
The reason: variables.
In my configuration, I store the specific applications I use in variables.
To give an example, I use kitty as my terminal, hence: `$terminal = kitty` is what's written in one of my configuration files.
Upon execution of the script, said variables are out of scope, and, thus, when the command is executed, nothing happens.
In short, another step needed to be taken: translate all the program variables before command execution.

Every relevant line in the file that stores program configurations is a simple assignment operation - just as in the above example.
Here's how the translation works: Select the relevant lines from the file using grep and format.
This yields a translation list:
- Command:
{% highlight bash linenos %}
PROGRAMMS_FILE="$HOME/.config/hypr/hyprland_programs.conf"
grep '^\$' "$PROGRAMMS_FILE" | \
    sed -E  -e 's/[[:space:]]+/ /g' \
            -e 's/ = /:/g'
{% endhighlight %}
- Output:
{% highlight bash linenos %}
{% include 2025-09-21-writing-a-shortcut-helper/snippet-09 %}
{% endhighlight %}

. Before executing the command, check if there are any variables inside the command.
If so, filter out the variable from the command, grep for the translation in the previously created translation list and use `sed` to replace the variable in the command with it's actual value 

{% highlight bash linenos %}
if [[ -n $(echo "$COMMAND" | grep -F "$") ]]; then
    TO_REPLACE=$(echo "$COMMAND" | awk -F '$' '{print "$"$2}')
    REPLACEMENT=$(echo "$TRANSLATION_LIST" | grep "$TO_REPLACE" | awk -F ':' '{print $2}')
    COMMAND=$(echo "$COMMAND" | sed "s/$TO_REPLACE/$REPLACEMENT/")
fi
{% endhighlight %}

### The entire script

{% highlight bash linenos %}
{% include 2025-09-21-writing-a-shortcut-helper/snippet-10 %}
{% endhighlight %}
![Shortcut helper showcase](/assets/images/shortcut_helper_showcase.gif)

## Designing your own script for you specific needs

The motivation behind this post was to show a detailed approach to designing your own shortcut helper.
Actually, not just a shortcut helper.
This concept can be used to contrive a plethora of tools such as a theme or wallpaper selector.
Feel free to make adjustments and tailor this script to your individual system.

Here's the approach I've taken in designing this script in short:

- Specify what you want and what the ouput should look like.
- Go into the file that holds the data you need to parse somehow and devise some format you can write your config file in, such that it is still comfortable to use but holds all the necessary information in one line.
- Step by step, use string manipulation tools to further and further get to the desired output.
- Display the output somehow and let the user - you - select one of the items.
- Translate the variables.
- In case you're aware of some better way of doing this, let me know.
