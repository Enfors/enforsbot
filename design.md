# EnforsBot design document

## Commands and parsers

- EnforsBot makes a CmdsLoader.

- CmdsLoader loads all the commands.

- EnforsBot makes a Parser.

- The Parser matches inputs to commands loaded by the CmdsLoader.

- EnforsBot calls the command identified by the Parser.
