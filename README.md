Introducing the ZWave Lock Manager plugin

Following the release of Indigo 7 which introduced Lock support, there was a lot of feedback about not being able to manage user PINs and other features of the Locks which many users were previously able to manage via the Vera plugin. 

Having already produced the ZWave Scene Controller plugin whilst Indigo 7 was in beta, I was already familiar with the new ZWave API hooks that were added in 7 - so with the help of a PDF posted by another user which gave the lock command syntax, I volunteered to write this plugin.

This plugin also supports many door/window sensors and keypads whether they're supported by Indigo or not yet. 

For those wanting to jump straight in, the latest download link is always at the bottom of this post. 

Current Features
•Set a user PIN
•Clear a user PIN
•Query a user PIN from a lock
•Supports 4-10 digit codes and RFID tags
•Log common status replies from the lock
•User count increased to 250 users, not just 10
•Added ability to set the Real Time Clock in the lock
•Added ability to set the Auto Lockout, Tamper and Operating Mode settings in the lock
•Added triggers for "User x locked/unlocked the door", "Invalid code entered" and "Deadbolt jammed"
•Ignores status reports from non-lock devices
•Adds support for ID Lock (Norwegian) and Zipato RFID Keypad
•Added support for any zwave lock even if it hasn't been defined by Matt/Jay as a lock
•Added several more triggers for who, what or how your lock was un/locked

Coming soon
•Update multiple codes at once
•Manage multiple locks at once
•Maintain user database with names and assigned codes

Planned for later
•Pass

Installation notes
This plugin creates a number of Actions under "Z-Wave Lock Manager actions". You can combine these with your own schedules, triggers and control panel buttons or simply execute them from the Indigo client. 

It should be noted that I don't actually have a ZWave lock to test against, so I'm coding blind - huge thanks to my beta testers for testing for me. 

When you install the plugin, you'll need to create a new device called ZWave Lock Manager > Door Lock for each lock you have. When you create it, it lists every Zwave device on your system, which might well be hundreds, but you only do this step once per lock so that doesn't matter. Thereafter, all events, triggers, actions etc present you with a list of Door Locks that you've defined, rather than a list of LockSubTypes or ZipatoKeypads etc. (For the purposes of my testing, I'm using a TKB plug socket as a pretend door lock, because I don't have any actual locks!)

If you are upgrading from v1.0.34 or earlier you will need to edit your existing actions and triggers once you've created your Door Lock devices, but that should only be necessary once.

Download link - v1.0.43

ZWaveLockManager.IndigoPlugin

Those who have seen me around the forums will know I usually participate in the forums at least daily if not several times; however please be aware this is usually from my iPhone when I'm away from my desk. I will endeavour to support this plugin as quickly as possible, but (as with everyone) I have busy periods of the year when I'm simply not at my desk long enough to do all I'd like to, including fixing or updating plugin code, even if you see me actively responding to other threads. 

Enjoy!

Peter