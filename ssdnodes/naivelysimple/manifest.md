# Naively Simple

We are an initiative that believes software should be straightforward,
efficient, easy to build and use. We also believe that the creation
and serving of software should be democratized. All these points lead
to several implications:

## The democratized software

People should be able to and encouraged to build their own software
and self-host their own services, on their own hardware. This is the
best way to ensure that we do not subject to the discretion of a
corporation (that they may discontinue a service at any time), and
that we own our data. In short, we should be in control of our own
software and services.

Historically the ability to build and host software has been
more-or-less limited to professionals, because of the knowledge
required to write good code, and manage a server. However gradually
over the recent years, this has stopped to be an issue (we are not
completely there yet, but it is progressing towards that) due to
cheaper hardware (not so much in the recent months but true overall)
and AI. Nowadays, one needs only little knowledge in programming in
order to write a usable service with the help of AI. Things like mini
PCs and the raspberry PI are cheap alternatives to servers in the
cloud. And AI can almost single-handedly set up and manage the server
for you.

Of course, by saying this we assume that we would be able to freely
run any compatible software on our own hardware, which seems to be
such an obvious assumption at the first glance. But another way of
saying this is: as adults, within the boundary of the law, nobody
should be able to tell us whether we can or cannot run a piece of
software on our own hardware. Is that so obvious still? Probably not,
because even if you are not an iPhone user, you probably have a friend
who uses an iPhone, and know that iPhone users do not have such a
basic freedom. iPhone users have to give Apple money and then let
*them* decide whether or not they can run their own software, on their
own hardware.

Android users have this freedom, [but maybe not for
long](https://android-developers.googleblog.com/2026/03/android-developer-verification.html).

## Straightforward and efficient software

We believe software should be “straightforward”. It should have the
least amount of dependencies possible, and be as easy to build and
understand as possible. Dependencies in general are fragile and
insecure. It is extremely frustrating to have the build fail because a
dependency has a version mismatch, or a bug with a certain version of
the compiler. Currently the usual way to solve this is to provide a
Docker image. We also shy away from using Docker images, because we
believe it signals that the build process is fragile and non-trivial —
the exact opposite of what we want. In the same vain, people usually
use Docker to deploy software, which we also do not recommend.
Software should be easy enough to deploy. In the ideal case, copying
the binary and a bunch of supporting files should be enough.

This naturally leads to our second point in this section. Software
should be efficient. This touches one of our fundamental believes that
the users’ hardware belongs to the users. We, the developers, do not
have the right to waste the users’ CPU cycles and memory, because,
again, they are not ours! This has some drastic implications. For
example, again, we shy away from Docker, because Docker inevitably
occupies large amount of disk and RAM space, and takes more CPU cycles
than nessesary. We also use “system language” (such as C++ and Rust)
as much as possible, because they usually produce binaries that are
more efficient. This also has the side-benefit of making the building
and deployment straightforward, because in most cases one could just
copy the binary and run on the target machine “baremetal”.
