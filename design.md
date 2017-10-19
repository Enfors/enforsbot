# EnforsBot design document

The bot is designed with a future voice interface in mind. All
interactions should feel natural if spoken aloud. However, with
Telegram, there is also the "buttons" interface, but that too should
be designed with speech in mind, where appropriate.

## Commands and parsers

- EnforsBot makes a CmdsLoader.

- CmdsLoader loads all the commands.

- EnforsBot makes a Parser.

- The Parser matches inputs to commands loaded by the CmdsLoader.

- EnforsBot calls the command identified by the Parser.

## Activity call stack

### Example: shutdown command

There are two activities: ShutdownActivity and AskYesOrNoActivity (for
verification of the shutdown command).

    "shutdown"
	-----------> ShutdownActivity
	             ------------------> AskYesOrNoActivity("Really?")

                                            "Really?"
    <------------------------------------------------
	
	"yes"
	-------------------------------> 

                                              "yes"
                 <-----------------------------------

                 "Okay, shutting down..."
    <-----------------------------------
	
* User sends "shutdown"


## Ideas

### Log / diary

It should be possible to take simple log / diary notes with the bot:

    -> log
	<- Making log entry. Enter done when done.
	-> Today was my last day in Sundsvall.
	-> It's been a long but interesting year.
	-> Now I'm looking forward to spending more time with family.
	-> Done
	<- Log entry saved.
	
An early version could simply save to a file. It should probably save
in Markdown format. Perhaps each sentence / line should be its own
paragraph, perhaps not.

### Notes

    -> note
	<- Taking note. Enter done when done.
	-> I have an idea.
	-> It shouldn't take long to implement.
	-> Done
	<- Please enter note title.
	-> my idea
	<- Note saved.
	
Alternative ways of starting the note-taking:

    -> make a note
	-> take a note
	-> make a note titled my awesome idea
	-> note with the title my awesome idea
	
