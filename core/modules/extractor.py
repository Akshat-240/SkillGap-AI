import PyPDF2

def extract_text_from_pdf(file_path): # Function to extract text from a PDF file
    text = ""
    try:
        with open(file_path, 'rb') as file: #read as binary
            reader = PyPDF2.PdfReader(file)
            

            for page in reader.pages:   # iterate through pages 
                page_text = page.extract_text() # extract text from each page

                if page_text:       # check if text is not None
                    text += page_text + "\n" # append text with a newline for separation

        if not text.strip():  # check if text is empty after stripping whitespace or images only
            print("No text found in the PDF.")
        
        return text
    
    except FileNotFoundError:
        return "Error: The file was not found at the specified path."
    
    except Exception as e:
        return f"Error processing PDF: {str(e)}"