/* 
 setxattrs - bubbaATbubba.org
 
 Properly sets sparse bundle extended attributes lost when rsyncing
 sparse bundle data to a platform that does not support extended 
 attributes.  This is only need when restoring/retrieving the
 bundle.
 
 To use, sync/copy all bundle files, then run this tool on the
 sparse bundle:
 % gcc -o setxattrs setxattrs.c
 % ./setxattrs mybackup.sparsebundle
 % xattr -l mybackup.sparsebundle
 
*/
 
#include <CoreFoundation/CoreFoundation.h>
#include <sys/xattr.h>
 
int main (int argc, const char * argv[]) {
 
   if (argc != 2) {
        printf("Usage: %s [sparse bundle directory]\n", argv[0]);
        printf("Sets extended attributes for sparse bundle disk image\n");
        return 0;
   }
   int sxr;
   int options = XATTR_NOFOLLOW;
   char theValue1[] = { 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00};
  char theValue2[] = { 0x59, 0x48, 0x60, 0x38,
            0x65, 0x7C, 0x09, 0x22, 0x33, 0xAD, 0xA5, 0x73,
            0x12, 0xAD, 0xF3, 0x7F, 0xEE, 0x90, 0x5B, 0x92};
 
   size_t   theSize1 = sizeof(theValue1);
   size_t   theSize2 = sizeof(theValue2);
 
   sxr = setxattr(argv[1], "com.apple.FinderInfo", (void *)theValue1, theSize1, 0, options);
   sxr = setxattr(argv[1], "com.apple.diskimages.fsck", (void *)theValue2, theSize2, 0, options);
 
   return 0;
}
