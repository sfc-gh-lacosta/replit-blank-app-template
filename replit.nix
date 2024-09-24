{pkgs}: {
  deps = [
    pkgs.libiconv
    pkgs.glibcLocales
    pkgs.xsimd
    pkgs.pkg-config
    pkgs.libxcrypt
  ];
}