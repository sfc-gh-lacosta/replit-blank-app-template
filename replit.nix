{ pkgs ? import <nixpkgs> {} }:
let
  # Define the Python version you want to use
  python = pkgs.python312;
  # Specify the Streamlit package
  streamlit = python.pkgs.streamlit;
in
  python.withPackages (p: [
    # Install Python packages from requirements.txt
    p.mkDerivation {
      name = "requirements";
      buildInputs = [p.python];
      buildPhase = ''
        ${p.python}/bin/pip install -r requirements.txt
      '';
    }
    # Streamlit installation
    streamlit
  ])
  # Define a 'run' command to start Streamlit
  { run = ''${python}/bin/streamlit run streamlit_app.py''; }