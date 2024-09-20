# LIGMA Annotates

LIGMA (Layered Image Graphical Markup Assistant) is a powerful annotation software for DICOM medical files.

## Features

- Best windowing system for DICOM files you can find anywhere
- Easy annotation of DICOM medical images
- Layered annotation system for complex markups (paint tool)
- User-friendly interface for efficient workflow
- Support for multiple annotation types (e.g., bounding boxes, polygons, landmarks)
- Export annotations in standard formats

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/itsalirezajalouli/ligma-annotates.git
   cd ligma-annotates
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run LIGMA Annotates, use the following command:

```
python main.py
```

## Documentation

There is nothing to be explained, just move the cursor and then -> clickity click.

## Contributing

I welcome contributions! but if you like to make a new one, fork it! kill it! tear it apart! I respect that.

## License

This project is licensed under the GLWTS License - see the [LICENSE](LICENSE) file for details.

## Contact

For support or queries, please contact us at billypushr@gmail.com.

./LIGMA_Annotates
│
├── main.py                 # Entry point
├── gui.py                  # Main GUI setup and window management
├── utils.py                # Utility functions (e.g., windowing gui handler)
├── image_loader.py         # Functions for loading DICOM 
├── annotation.py           # Annotation logic (e.g., mask creation, segmentation)
└── save_manager.py         # Npy, NIfTI, CSV, Json mask saving