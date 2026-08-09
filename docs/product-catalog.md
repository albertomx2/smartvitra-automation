# Product Catalog

## Directory structure

Each product has its own directory:

assets/catalog/<product>/

Required files:

- product.json
- source.pdf

Future optional directory:

- images/

## product.json

Required core fields:

- product_code
- name
- category
- source_document
- properties
- benefits

## Adding a new product

1. Create a new product directory.
2. Add the original technical PDF as source.pdf.
3. Create product.json.
4. Run the complete test suite.
5. Verify that the product loads correctly.

Application code must not be modified simply to add a product.

## Source of truth

Technical properties must be supported by the original manufacturer technical documentation.

Generated commercial content must never override technical product data.
