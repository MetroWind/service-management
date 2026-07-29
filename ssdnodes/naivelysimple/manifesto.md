# Naively Simple

Naively Simple is built around a simple idea: software should be
straightforward, efficient, easy to build, and easy to run. People should
also be free to write their own software and host their own services.

## Software for everyone

People should be able, and encouraged, to build their own software and host
services on hardware they control. This is the best way to avoid depending
entirely on a corporation that may discontinue a service or change its
terms. It also lets us keep possession of our data. We should control the
software and services we rely on.

Until recently, writing and hosting good software required enough
specialized knowledge that it was mostly limited to professionals. That
barrier has started to fall. Mini PCs and devices such as the Raspberry Pi
make home servers affordable. AI-assisted tools can help people learn,
write code, and troubleshoot unfamiliar systems.

These tools do not remove the need to understand security, backups, or the
code being run. They do, however, make it easier for more people to begin.
We are not all the way there, but running a useful service no longer has to
start with years of professional experience or a rented cloud server.

All of this assumes that we are free to run compatible software on
hardware we own. That sounds like such an obvious assumption that it
should not need to be written down. But put differently: as adults,
within the boundaries of the law, nobody should be able to tell us
whether we may run a piece of software on our own hardware.

Is that still obvious? Apparently not.

An iPhone owner cannot simply copy an arbitrary native program onto
the phone, install it, and keep running it as one would on a
general-purpose computer. Apple’s supported development workflow
requires Apple-issued provisioning profiles. Keeping your own software
installed without continually repeating the process requires a paid
developer membership.

In other words, an iPhone user pays Apple for the hardware, then has to pay
Apple again for the privilege of letting Apple decide whether they may run
their own software on it. The important word is "decide," not "allow."
Apple reserves the right to say no.

We also reject the term "sideloading." Installing a program obtained
directly from its developer is simply installing software. An app
store is an optional intermediary, not the natural owner of the
installation process. Stores can provide useful discovery, updates,
and security checks, but they should never have exclusive authority
over what runs on the user’s hardware.

Android has historically given users more control, but Google’s recent
developer verification system complicates that freedom.

## Straightforward and efficient software

Software should be straightforward. It should have as few dependencies as
practical, and it should be easy to build and understand. Dependencies are
not free. Every one is another place where versions can conflict, builds
can fail, vulnerabilities can appear, or maintenance can stop.

The usual answer to a difficult build is to provide a Docker image. We shy
away from that. If a container is the only practical way to build or deploy
a small service, then the build and deployment are already fragile and
nontrivial. That is the exact opposite of what we want.

Docker has its uses. Hiding an incomprehensible build is not one of
them. In the ideal case, deploying software should mean copying a
binary and a few supporting files.

Software should also be efficient. The user’s hardware belongs to the
user, not the developer. Developers do not have the right to waste the
user’s CPU time, memory, storage, or electricity merely because doing
so is convenient for them. Those resources are owned by the users, not
the developers!

The user’s hardware is not a playground for the developers, either.
Fancy visual effects and unnecessary interactions do not become
worthwhile merely because they are fun to implement or impressive in a
demo. An interface should help the user operate and understand the
software. It should not exist so that the developer can show off.

This is also why we shy away from Electron. Shipping an entire browser
runtime with a desktop application may be convenient for the
developer, but the user pays for that convenience with memory,
storage, CPU time, and battery life. Sometimes that trade is
justified, but it should never be treated as free or the default
choice.

These preferences affects our choice of tools. We use system languages
such as C++ and Rust when they suit the project because they can
produce compact, efficient, self-contained binaries. They also make
simple deployment possible: in many cases, a user can copy the binary
to the target machine and run it directly.

Efficiency is not a benchmark contest, and straightforward software is
not software with no dependencies at all. Both are matters of
*respect*. A program should ask only for the complexity and resources
its job actually requires.
