{
  description = "Python shell";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs, ... }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forEachSupportedSystem =
        f:
        nixpkgs.lib.genAttrs supportedSystems (
          system:
          f {
            pkgs = import nixpkgs { inherit system; };
          }
        );
    in
    {
      devShells = forEachSupportedSystem (
        { pkgs }:
        {
          name = "python";
          default = pkgs.mkShell {
            packages = with pkgs; [
              (pkgs.python3.withPackages (
                python-pkgs: with python-pkgs; [
                  pip
                ]
              ))

              pyright # lsp
              black # formatter
            ];
            shellHook = ''
              if [ ! -d ".venv" ]; then
                  python3 -m venv .venv
              fi
              source .venv/bin/activate
            '';
          };
        }
      );
    };
}
