#!/usr/bin/python3

init = 'systemd'

print("Checking if cam_collect_images is running:")
if init == 'systemd':
    print(`systemctl status cam_collect_images | grep Active`, "\n"
}
else {
    print(`status cam_collect_images`, "\n"
}

print("Are we building?\n"
res = `pidof -x build_time_lapse.pl`
if ( $res ne "" ) {
    print("Yes!  Process: $res\n"
}
else {
    print("Nope\n\n"
}
#print("Are we building?\n"
#print `ps auwwx | grep build_time_lapse.pl`, "\n"

print("Is there a push happening:\n"
$res =  `pidof -x push2youtube.py`
if ( $res ne "" ) {
    print("Yes!  Process: $res\n"
}
else {
    print("Nope\n\n"
}
#print("Is there a push happening:\n"
#print `ps auwwx | grep push2youtube_2015.py`, "\n"

print("Where is the sun?\n")
print `/usr/local/cam/bin/sun.pl`, "\n"
