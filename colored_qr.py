import qrcode
import qrcode.image.svg
import os
import xml.etree.ElementTree as ET
import zipfile
from tqdm import tqdm

def generate_colored_qr_code_svg(data: str, file_name: str, qr_color: str = "#000000", background_color: str = "#FFFFFF"):
    """
    Generates a QR code in SVG format with a specified foreground and background color,
    ensuring the fill attribute is correctly set in the SVG XML.

    Args:
        data (str): The data to encode in the QR code (e.g., a URL, text).
        file_name (str): The name of the SVG file to save (e.g., "my_qrcode.svg").
        qr_color (str): The hexadecimal color code for the QR code modules (e.g., "#FF0000" for red).
                        Defaults to a shade of green.
        background_color (str): The hexadecimal color code for the background of the QR code.
                                Defaults to white.
    """
    try:
        # Create a QRCode object
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
            image_factory=qrcode.image.svg.SvgPathImage # Use SvgPathImage for a single path
        )

        # Add data to the QR code
        qr.add_data(data)
        qr.make(fit=True)

        # Generate the SVG image. The back_color is usually applied to the <rect> background element.
        img = qr.make_image(back_color=background_color)


        svg_string = img.to_string()

        # --- XML Manipulation to ensure correct fill color ---
        # Parse the SVG string
        root = ET.fromstring(svg_string)

        # Define the SVG namespace for robust parsing
        namespace = "{http://www.w3.org/2000/svg}"

        # Find the main path element that represents the QR code modules.
        # This is typically the first <path> element in the SVG.
        path_element = root.find(f".//{namespace}path")

        if path_element is not None:
            # Set the fill attribute of the path element to the desired QR color
            path_element.set("fill", qr_color)
        else:
            print(f"Warning: Could not find the main path element in {file_name}. QR code color might not be applied.")

        # If there's a background rectangle, ensure its fill is set too
        rect_element = root.find(f".//{namespace}rect")
        if rect_element is not None:
            rect_element.set("fill", background_color)

        # Serialize the modified XML tree back to a string
        modified_svg_string = ET.tostring(root, encoding='unicode', xml_declaration=True)

        # Save the modified SVG to a file
        with open("output/"+file_name, "w") as f: # Open in text mode for unicode string
            f.write(modified_svg_string)

    except Exception as e:
        print(f"An error occurred while generating '{file_name}': {e}")

def generate_multiple_qr_codes(
    num_codes: int,
    qr_color: str = "#304778", # Default blue
    background_color: str = "#FFFFFF", # Default Alice Blue
    valid_uses: int = 15,
    volume: int = 50,
    end_date: str = "2026.12.31"
):
    if num_codes <= 0:
        print("Number of QR codes to generate must be a positive integer.")
        return

    print(f"\n--- Generating {num_codes} QR codes ---")

    for i in tqdm(range(1, num_codes + 1), desc="Generating QR codes"):
        # Create the payload dictionary for the current QR code
        payload = f"M-{valid_uses}-{i:08d}-{volume}-{end_date}-SECD-23FF45EE"

        # Generate a unique file name for each QR code
        # Uses f-string formatting to pad the counter with leading zeros (e.g., 001, 010)
        file_name = f"{payload}.svg"

        # Generate the QR code with the JSON payload
        generate_colored_qr_code_svg(payload, file_name, qr_color, background_color)

    print(f"\n--- Finished generating {num_codes} QR codes ---")

def zip_output_files(output_folder, zip_file_name, format):
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_folder):
            for file in files:
                if file.endswith(f".{format}"):
                    zipf.write(os.path.join(root, file), arcname=file)

def clean_output_folder(output_folder):
    for root, _, files in os.walk(output_folder):
        for file in files:
            os.remove(os.path.join(root, file))

if __name__ == "__main__":
    # --- Example Usage for generating multiple QR codes ---
    num_qr_codes_to_generate = 1000

    # You can customize these parameters
    my_qr_color = "#304778" # Emerald Green
    my_bg_color = "#FFFFFF" # White
    my_valid_uses = 15
    my_volume = 50
    my_end_date = "26.12.31" # Example end date

    generate_multiple_qr_codes(
        num_qr_codes_to_generate,
        qr_color=my_qr_color,
        background_color=my_bg_color,
        valid_uses=my_valid_uses,
        volume=my_volume,
        end_date=my_end_date
    )

    zip_output_files("output", f"QR-{my_valid_uses}-{my_volume}-{my_qr_color}-{num_qr_codes_to_generate}.zip", "svg")

    clean_output_folder("output")