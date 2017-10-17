# EnforsBot design document

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
