"""
Preprocessing

Haystack includes a suite of tools to extract text from different file types, normalize white space
and split text into smaller pieces to optimize retrieval.
These data preprocessing steps can have a big impact on the systems performance and effective handling of data is key to getting the most out of Haystack.

Ultimately, Haystack pipelines expect data to be provided as a list documents in the following dictionary format:

docs = [
    {
        'text': DOCUMENT_TEXT_HERE,
        'meta': {'name': DOCUMENT_NAME, ...}
    }, ...
]

This tutorial will show you all the tools that Haystack provides to help you cast your data into the right format.
"""

import logging

# We configure how logging messages should be displayed and which log level should be used before importing Haystack.
# Example log message:
# INFO - haystack.utils.preprocessing -  Converting data/tutorial1/218_Olenna_Tyrell.txt
# Default log level in basicConfig is WARNING so the explicit parameter is not necessary but can be changed easily:
logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)

# Here are the imports we need
from pathlib import Path

from haystack.nodes import TextConverter, PDFToTextConverter, DocxToTextConverter, PreProcessor
from haystack.utils import convert_files_to_docs, fetch_archive_from_http


def tutorial8_preprocessing():
    # This fetches some sample files to work with

    doc_dir = "data/tutorial8"
    s3_url = "https://s3.eu-central-1.amazonaws.com/deepset.ai-farm-qa/datasets/documents/preprocessing_tutorial8.zip"
    fetch_archive_from_http(url=s3_url, output_dir=doc_dir)

    """
    ## Converters
    
    Haystack's converter classes are designed to help you turn files on your computer into the documents
    that can be processed by the Haystack pipeline.
    There are file converters for txt, pdf, docx files as well as a converter that is powered by Apache Tika.
    The parameter `valid_languages` does not convert files to the target language, but checks if the conversion worked as expected.
    """

    # Here are some examples of how you would use file converters

    converter = TextConverter(remove_numeric_tables=True, valid_languages=["en"])
    doc_txt = converter.convert(file_path=Path(f"{doc_dir}/classics.txt"), meta=None)[0]

    converter = PDFToTextConverter(remove_numeric_tables=True, valid_languages=["en"])
    doc_pdf = converter.convert(file_path=Path(f"{doc_dir}/bert.pdf"), meta=None)[0]

    converter = DocxToTextConverter(remove_numeric_tables=False, valid_languages=["en"])
    doc_docx = converter.convert(file_path=Path(f"{doc_dir}/heavy_metal.docx"), meta=None)[0]

    # Haystack also has a convenience function that will automatically apply the right converter to each file in a directory.

    all_docs = convert_files_to_docs(dir_path=doc_dir)

    """
    
    ## PreProcessor
    
    The PreProcessor class is designed to help you clean text and split text into sensible units.
    File splitting can have a very significant impact on the system's performance.
    Have a look at the [Preprocessing](https://haystack.deepset.ai/docs/latest/preprocessingmd)
    and [Optimization](https://haystack.deepset.ai/docs/latest/optimizationmd) pages on our website for more details.
    """

    # This is a default usage of the PreProcessor.
    # Here, it performs cleaning of consecutive whitespaces
    # and splits a single large document into smaller documents.
    # Each document is up to 100 words long and document breaks cannot fall in the middle of sentences
    # Note how the single document passed into the document gets split into 5 smaller documents

    preprocessor = PreProcessor(
        clean_empty_lines=True,
        clean_whitespace=True,
        clean_header_footer=False,
        split_by="word",
        split_length=100,
        split_respect_sentence_boundary=True,
    )
    docs_default = preprocessor.process([doc_txt])
    print(f"\nn_docs_input: 1\nn_docs_output: {len(docs_default)}")

    """
    ## Cleaning
    
    - `clean_empty_lines` will normalize 3 or more consecutive empty lines to be just a two empty lines
    - `clean_whitespace` will remove any whitespace at the beginning or end of each line in the text
    - `clean_header_footer` will remove any long header or footer texts that are repeated on each page
    
    ## Splitting
    By default, the PreProcessor will respect sentence boundaries, meaning that documents will not start or end
    midway through a sentence.
    This will help reduce the possibility of answer phrases being split between two documents.
    This feature can be turned off by setting `split_respect_sentence_boundary=False`.
    """

    # Not respecting sentence boundary vs respecting sentence boundary

    preprocessor_nrsb = PreProcessor(split_respect_sentence_boundary=False)
    docs_nrsb = preprocessor_nrsb.process([doc_txt])

    print("\nRESPECTING SENTENCE BOUNDARY:")
    end_text = docs_default[0].content[-50:]
    print('End of document: "...' + end_text + '"')

    print("\nNOT RESPECTING SENTENCE BOUNDARY:")
    end_text_nrsb = docs_nrsb[0].content[-50:]
    print('End of document: "...' + end_text_nrsb + '"')
    print()

    """
    A commonly used strategy to split long documents, especially in the field of Question Answering,
    is the sliding window approach. If `split_length=10` and `split_overlap=3`, your documents will look like this:
    
    - doc1 = words[0:10]
    - doc2 = words[7:17]
    - doc3 = words[14:24]
    - ...
    
    You can use this strategy by following the code below.
    """

    # Sliding window approach

    preprocessor_sliding_window = PreProcessor(split_overlap=3, split_length=10, split_respect_sentence_boundary=False)
    docs_sliding_window = preprocessor_sliding_window.process([doc_txt])

    doc1 = docs_sliding_window[0].content[:200]
    doc2 = docs_sliding_window[1].content[:100]
    doc3 = docs_sliding_window[2].content[:100]

    print('Document 1: "' + doc1 + '..."')
    print('Document 2: "' + doc2 + '..."')
    print('Document 3: "' + doc3 + '..."')


if __name__ == "__main__":
    tutorial8_preprocessing()

# This Haystack script was made with love by deepset in Berlin, Germany
# Haystack: https://github.com/deepset-ai/haystack
# deepset: https://deepset.ai/
