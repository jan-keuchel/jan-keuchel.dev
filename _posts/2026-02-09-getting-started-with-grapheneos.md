---
title: Getting started with GrapheneOS
date: 2026-02-09
language: en
ongoing: false
published: true
---

## Why I decided to switch to GrapheneOS
I never really liked the idea that my phone is continually collecting data about how I behave.
At the same time, I never read into the topic and just went with what I heard over the years.
Then, I came across a [research paper](https://digitalcontentnext.org/wp-content/uploads/2018/08/DCN-Google-Data-Collection-Paper.pdf) which is addressing the issue more precisely.
It most definitely is worth a read.
It's what made me want to switch to GrapheneOS.

{: .highlight-block .highlight-note }
**Disclaimer**: I'm by no means experienced with GrapheneOS and just recently made the switch.
I just thought it would be useful to provide other people, who might be considering whether or not to switch, with a resource that gives them a "walkthrough" on how to get to a basic setup.
In short: I'm writing the document I would have liked to have a few days ago.

## Installation

### Choosing a device
In order to install GrapheneOS on your phone you need to have one of the [supported phones](https://grapheneos.org/faq#supported-devices).
I personally went with a Pixel 8, as it is the first device to receive 7 years of support - up until October 2030.
How long different devices will be supported is listed [here](https://grapheneos.org/faq#device-lifetime).

### Installing GrapheneOS
I didn't have any trouble with the installation so I'm not going to write down what I did.
It would simply be a periphrasis of the [installation instructions](https://grapheneos.org/install/web).

The only thing worth mentioning is that - though your device will tell you this - in order to enable OEM unlocking, you will need to have a network connection established.

I first went through the default installation process without being connected to the internet as it is quicker - this I do recommend.
You can turn on Wi-Fi if the default OS is installed and then simply reboot the device.
After doing so, you should be able to enable OEM unlocking.

## Setting up the phone
Here is what I would do when setting up the phone anew:

### Settings
To begin with, you'll start in the `Owner` profile.

Here are some of my settings:

#### Network and Internet
* Internet > Network preferences > Turn on Wi-Fi automatically: **`false`**
* Internet > Network preferences > Notify for public networks: **`true`**
* Internet > Network preferences > Allow WEP networks: **`false`**
* Private DNS > Hostname: **`dns.adguard-dns.com`**

#### Connected devices
* Connection preferences > Printing > Default print service: **`false`**

#### Notifications
* Notifications on lock screen: **`Compact`**
* Notifications on lock screen > Show sensitive content: **`false`**
* Notification cooldown > Use notification cooldown: **`true`**

#### Display
* Always-on display: **`false`**
* Screen timeout: **`2 minutes`**

#### Battery
* Battery Saver > Use Battery Saver: **`true`**
* Charging optimisation > Limit to 80%: **`true`**
* Battery percentage: **`true`**

#### System
* Gestures > Navigation mode: **`3-button navigation`**
* Gestures > Lift to check phone: **`false`**
* Users > Allow user switch: **`true`**

#### About phone
* Device name: **`<phone_name>`**

#### Security and privacy
* Device unlock > Screen lock: **`PIN`**
* Device unlock > Screen lock > Auto-confirm unlock: **`false`**
* Device unlock > Screen lock > Scramble PIN input layout: **`true`**
* Device unlock > Screen lock > Enhanced PIN privacy: **`true`**
* Device unlock > Screen lock > Allow camera access when locked: **`false`**
* Device unlock > Screen lock > Power button instantly locks: **`true`**
* Device unlock > Fingerprint > Unlock your phone: **`true`**
* Device unlock > Fingerprint > Verify that it's you in apps: **`true`**
* Privacy controls > Camera access: **`false`**
* Privacy controls > Microphone access: **`false`**
* Privacy controls > Show clipboard access: **`true`**
* Privacy controls > Show passwords: **`false`**
* Privacy controls > Location access > Use location: **`false`**
* Exploit protection > Auto reboot: **`12 hours`**
* Exploit protection > USB-C port: **`Charging-only when locked`**
* Exploit protection > Turn off Wi-Fi automatically: **`5 minutes`**
* Exploit protection > Turn off Bluetooth automatically: **`5 minutes`**
* More security and privacy > Allow Sensors permission to apps by default: **`false`**
* More security and privacy > Save screenshot timestamp to EXIF: **`false`**

### Quick access to frequently used settings
As I have to toggle some of these settings frequently and don't want to scroll through the settings, I recommend configuring your "Quick Settings Menu".
I personally have the sensor permissions for the microphone, camera and GPS directly accessible in there.

### User profile structure
I wanted to separate the things I do on my phone into different user profiles.
You can create different user profiles at Settings > System > Users > Add user.

#### Profile 0: `Owner`
First of all, don't use the `Owner` profile as your daily driver.
The profile can't be deleted and set up anew - except for reinstalling the OS.
Hence, this profile is solely used for administration purposes such as managing the different user profiles and configuring certain settings that other users aren't allowed to modify.

#### Profile 1: `Main`
This is the profile I spend most of the time in.
In here, I installed virtually all the apps I use.
For me, it was important to capsule all Google related applications into a separate user profile and to keep the `Main` profile Google free.
I will touch on how you can install different applications in the next section.

#### Profile 2: `Banking`
My banking apps rely on the Google Play Store.
As banking is a quite sensitive topic I didn't want to mix it with other applications installed via the Play Store.
Hence, I separated it into its own profile.

#### Profile 3: `Google`
As the name suggests, in here are all the apps installed via the Google Play Store.
For me, only two apps are in here: WhatsApp (as some of my contacts don't have Signal) and Google Maps.

#### Notifications
In order to receive notifications from user profiles that you are currently not using, it is possible to allow notification forwarding to the current user.
This can be done from within the respective user profile at:

Settings > System > Users > Send notifications to current user: **`true`**.

I enabled this setting for the user profiles `Owner`, `Main` and `Banking`.

{: .highlight-block .highlight-note }
This means that I won't be notified if someone writes me a message via WhatsApp. I'm gonna have to manually switch profiles into the `Google` profile to check it.


### Installing applications
You might have realized that, by default, there are not a lot of apps installed.
To install the necessary apps, I used:
* The GrapheneOS `App Store`
* `Obtainium`
* `Aurora Store`
* `Google Play Store`

#### Installing applications across profiles
The different user profiles are not able to share apps between them.
This means that in order to have, say, KeePassDX available on every user profile, it has to be installed on every single one of them.

Luckily, it is possible to "push" applications from the `Owner` to other user profiles. 
That way you can install the applications you need on every user profile in the `Owner` and then push them over.
Obviously, this makes things quicker.

#### Obtainium, KeePassDX and Syncthing-Fork in `Owner`
I use KeePassDX as my password manager.
In order to sync the `.kdbx` file between laptop and phone, I use SyncThing.

Open source apps can be installed directly from the source using Obtainium.
All that Obtainium needs to install a given app, is, for example, its GitHub repository.

Here are the repositories of [KeePassDX](https://github.com/Kunzisoft/KeePassDX/releases) and [Syncthing-Fork](https://github.com/researchxxl/syncthing-android/releases) that I used.

Now, how is Obtainium installed?
Via the `.apk` file from the web.
The latest release can be found on [GitHub](https://github.com/ImranR98/Obtainium/releases).
You will have to give Vanadium - GrapheneOS' browser - permissions to be able to install applications on your device.

Once Obtainium is installed on the `Owner` profile it can be used to install KeePassDX and Syncthing-Fork.

In the case of KeePassDX, I was prompted with a choice between a "free" and a "libre" version.
I went with the latter one.

These are the only applications I have installed on the `Owner` profile.

In order to push them to the other user profiles got to:
Settings > System > Users > `<User>` > Install available apps > `select apps`.

I decided to push KeePassDX and Syncthing-Fork to every other profile and the Obtainium app store to `Main`.

#### Other applications in `Main`

Other open source applications can be installed using Obtainium:
* [Acode](https://github.com/acode-foundation): Plain text editor.
* [Gallery](https://github.com/IacobIonut01/Gallery/releases/tag/4.0.2)
* [K-9 Mail](https://github.com/thunderbird/thunderbird-android)
* [Music Player](https://github.com/Anrimian/music-player)
* [Proton Calendar](https://github.com/ProtonMail/proton-calendar/releases?after=v4.1.13)
* [Signal](https://apps.obtainium.imranr.dev) (Search for "Signal" and click "Add to Obtainium")

In order to install some closed source apps without using Google Play I used [Aurora Store](https://www.auroraoss.com/files/AuroraStore/Release).
To install it, download the latest `.apk`.

From within Aurora Store you can download virtually all the applications you could download in the Google Play Store without having to log into a Google account. 
Some apps won't work properly as they require Google Play running in the background.
That means, you're gonna have to download and test the apps to see if they work properly.

Luckily, I didn't have any issues with the apps I needed.

With that, the `Main` profile is set up to work with all the applications I need on a daily basis.

#### Installing Banking applications in `Banking`
This is pretty easy.
As Google Play is required to have the banking applications run properly, they can be installed via the Google Play Store.
The Google Play Store can be installed using the GrapheneOS App Store.
Done.

[Here](https://privsec.dev/posts/android/banking-applications-compatibility-with-grapheneos/) is a list of banking apps and their compatibility on GrapheneOS.

Here, too, I didn't have any issues and every app worked as you'd expect it to.

#### Installing remaining applications in `Google`
I sometimes use Google Maps and WhatsApp.
The latter one mostly because some people continue to use WhatsApp and don't want to use Signal.
As I don't want to cut off communication, I installed WhatsApp in my `Google` user profile.
I did this similar to the banking apps: Install Google Play via GrapheneOS' App Store, then install applications as usual.

### Fixing some issues I had

#### Fingerprint reader not working properly
I had some issues with the fingerprint reader: It didn't detect my finger properly.
In order to fix that issue, I added the same finger again as another fingerprint.
This fixed the issue and my finger now gets detected virtually every time.

### Things I need to look into
* How do I create a backup of the system configuration in order to restore it on a new device?
* How do I backup data?
* How do I sync data between the user profiles (`.kdbx` database)?
* How do export settings from one user profile and apply them to another such that I don't have to do the same thing 4 times?

### My experience so far
My main worries before switching to GrapheneOS were about the banking apps working properly.
All I can say thus far is that every app works without issues.
Everything went smoothly and I strongly recommend you try it out for yourself if you have the chance to do so.

I was truly impressed by how easy the OS installation process was.
Just clicking a few buttons in the Web UI and you're done!

I will upload another blog post in a few months to give an update on how things are going and - hopefully - answer the above questions.
