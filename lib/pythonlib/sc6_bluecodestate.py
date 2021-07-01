# package SC6::Cam::BlueCodeState;
#
# use strict;
# use warnings;
# use DateTime;
# use File::Copy;
# use GD;
# use SC6::Cam::General;
# use SC6::Cam::GStore;
#
# sub new {
#     class = shift;
#     self = {
#         _mode => shift,
#         _dryrun => shift,
#     ]
#
#     prime(self);
#
#     bless self, class;
#     return self;
# }
#
# sub checkBluecode {
#     my (self, new_image) = @_;
#
#     new_bluecode = new_image->getBluecode();
#     current_bluecode = self->getConfirmedBluecode();
#
#     print "checking bluecode, new: new_bluecode old: ", current_bluecode, "\n";
#     if ( new_bluecode > current_bluecode ) {
#         print "new bluecode: new_bluecode old: ", current_bluecode, "\n";
#         www_image_50pct = new_image->{_www_image_50pct]
#         www_image_orig = new_image->{_www_image_orig]
#         self.bluecode} = new_bluecode;
#         save_is_blueist_stash(self, new_image);
#         save_is_blueist_local(self, www_image_50pct, www_image_orig);
#         cache(self);
#         return 1;
#     }
#     return 0;
# }
#
# sub getConfirmedBluecode {
#     my (self) = @_;
#     blue_code_file = get_www_dir("", main::mode) . self.config['BlueCode}->{'File']
#
#     new_file_time = (stat(blue_code_file))[9];
#     if ( ! defined self.blue_change_time} || new_file_time != self.blue_change_time} ) {
#         if ( -f blue_code_file ) {
#             self.bluecode} = readBluecodeFile(blue_code_file);
#             self.blue_change_time} = (stat(blue_code_file))[9];
#         }
#         else {
#             self->prime();
#         }
#     }
#     return self.bluecode]
# }
#
# sub getBluecode {
#     my (self) = @_;
#
#     return self.bluecode]
# }
#
# sub setBluecode {
#     my (self, bc) = @_;
#
#     self.bluecode} = bc;
# }
#
# sub clear {
#     my ( self ) = @_;
#
#     blue_code_file = get_www_dir("", main::mode) . self.config['BlueCode}->{'File']
#     priming_bluecode = self.config['BlueCode}->{'PrimingValue']
#     if ( -f blue_code_file ) {
#         unlink(blue_code_file) or die "Can't unlink blue_code_file: !\n";
#     }
#     self.bluecode} = priming_bluecode;
#     self.blue_change_time} = 0;
#     return self.bluecode]
# }
#
# sub save_is_blueist_stash {
#     my ( self, new_image ) = @_;
#
#     stash_dir = get_image_dir(new_image->{_dt}, "stash", main::mode);
#     stash = stash_dir . "/" . self.bluecode} . ".jpg";
#     current_link = stash_dir . "/" . "current.jpg";
#     image = new_image->{_output]
#     print "going to symlink image to stash\n";
#     symlink(image, stash) or die "Can't symlink image to stash: !\n";
#     
#     if ( -f current_link ) {
#         unlink(current_link) or die "Can't unlink current_link:!\n";
#     }
#     print "going to symlink image to current_link\n";
#     symlink(image, current_link) or die "Can't symlink image to current_link: !\n";
# }
#
# sub save_is_blueist_local {
#     my ( self, bf_50pct, bf_orig ) = @_;
#     bc = self.bluecode]
#     blueist_file_50pct = get_www_dir("", main::mode) . self.config['BlueCode}->{'BlueistImage'} . "_50pct";
#     blueist_file_orig = get_www_dir("", main::mode) . self.config['BlueCode}->{'BlueistImage'} . "_orig";
#
#     # local copies
#     copy(bf_50pct, blueist_file_50pct) or die "Can't copy bf_50pct to blueist_file_50pct: !\n";
#     copy(bf_orig, blueist_file_orig) or die "Can't copy bf_orig to blueist_file_orig: !\n";
#     print "Bluecode copy: bf_50pct to blueist_file_50pct\n" if ( main::debug );
#     print "Bluecode copy: bf_orig to blueist_file_orig\n" if ( main::debug );
#
# }
#
# sub cache {
#     my (self) = @_;
#
#     blue_code_file = get_www_dir("", main::mode) . self.config['BlueCode}->{'File']
#     open F, ">blue_code_file" or die "Can't open blue_code_file!\n";
#     print F self.bluecode]
#     print "writing bluecode file locally.  Current bluecode: ", self.bluecode}, "\n" if ( main::debug );
#     self.blue_change_time} = (stat(blue_code_file))[9];
#     close F;
# }
#
# sub prime {
#     my (self) = @_;
#
#     priming_bluecode = self.config['BlueCode}->{'PrimingValue']
#     blue_code_file = get_www_dir("", main::mode) . self.config['BlueCode}->{'File']
#
#     if ( -f blue_code_file ) {
#         self.bluecode} = readBluecodeFile(blue_code_file);
#         print "Bluecode file (blue_code_file) found, priming with ", self.bluecode}, "\n" if ( main::debug );
#         return self;
#     }
#     else {
#         print "No bluecode file, priming with priming_bluecode\n" if ( main::debug );
#         self.bluecode} = priming_bluecode;
#         return self;
#     }
# }
#
# sub readBluecodeFile {
#     file = shift;
#     open F, file or die "Can't open file !\n";
#     in = <F>;
#     chomp(in);
#     return in;
# }
#
