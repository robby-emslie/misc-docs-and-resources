/*
    The csvExtractAndTransform.js utility is a primitive ETL tool for CSV-sourced
    data. It is designed to extract data from a CSV string, transform specified fields
    and/or render them into a new field(s) based on a definition and return the
    transformed data as JSON.

    The utility is written for the n8n automation platform, but can be adapted to
    other systems and architectures, accordingly.

    DEV TO-DO:
        - Enhance CSV parsing to handle quoted strings, special characters, etc.
        - Expand options for extraction types
        - Implement JSON ingest (as alternative to CSV)
        - Anything else that comes to mind...?

    INPUTS:
        items[0].json.csvString - the stringified contents of a CSV source
        items[0].json.definition - the extraction definition, including transformation
                                    formulae, in JSON format
    
    DEFINITION FORMAT:
    aDefinition = {
        "sourceType": "csv",
        "company": "Acme, Inc.",
        "fileType": "account_list",
        "rawFields": {  // rawFields define those fields which are a 1:1 ingest without transformation
            // "sourceFieldName": "outputFieldName",
            "firstName": "firstName",
            "lastName": "lastName",
            "phone": "phoneNumber",
            "email": "emailAddress",
            "company": "companyName",
            "employeeId": "id"
        },
        "composedFields": [ // composedFields are those which are constructed from multiple fields in
            {               // the source and output as a single field, based on the formula provided
                "fieldName": "agentId",
                "sourceFields": [
                    {
                        "field": "lastName",
                        "extractionType": "first.3", // types: first.x, last.x, "regex-as-string", full_field
                        "extractionFormula": null,
                        "fieldId": "field1"
                    },
                    {
                        "field": "employeeId",
                        "extractionType": "full_field",
                        "extractionFormula": null,
                        "fieldId": "field2"
                    }
                ],
                "fieldConstructor": "{field1}{field2}"
            }
        ]
    };
*/

const csvString = items[0].json.csvString;
const definition = items[0].json.definition

/* Parse out CSV (basic) */
function parseCSV(csv) {
    const lines = csv.trim().split('\n');
    const headers = lines[0].split(',');

    return lines.slice(1).map(line => {
        const values = line.split(',');
        const obj = {};
        headers.forEach((h, i) => {
            obj[h.trim()] = (values[i] || '').trim();
        });
        return obj;
    });
}

/* Extraction logic */
function extractValue(value, extractionType, extractionFormula) {
    if (!value) return '';

    if (!extractionType || extractionType === 'all' || extractionType === 'full_field') {
        return value;
    }

    if (extractionType.startsWith('first.')) {
        const n = parseInt(extractionType.split('.')[1], 10);
        return value.substring(0, n);
    }

    if (extractionType.startsWith('last.')) {
        const n = parseInt(extractionType.split('.')[1], 10);
        return value.slice(-n);
    }

    if (extractionType === 'regex') {
        try {
            const regex = new RegExp(extractionFormula);
            const match = value.match(regex);
            return match ? match[0] : '';
        } catch(e) {
            return '';
        }
    }

    return value;
}

/* Composed field builder */

function buildComposedField(row, composedDef) {
    let constructed = composedDef.fieldConstructor;
    
    composedDef.sourceFields.forEach(sf => {
        const rawVal = row[sf.field];
        const extracted = extractValue(
            rawVal,
            sf.extractionType,
            sf.extractionFormula
        );

        const placeholder = `{${sf.fieldId}}`;
        constructed = constructed.replace(
            new RegExp(placeholder, 'g'),
            extracted
        );
    });

    return constructed;
}

// Extract
const rows = parseCSV(csvString);

// Transform
const output = rows.map(row => {
    const result = {};

    // raw fields
    if (definition.rawFields) {
        Object.entries(definition.rawFields).forEach(([outKey, sourceKey]) => {
            result[outKey] = row[sourceKey] || null;
        });
    }

    // built fields
    if (definition.composedFields) {
        definition.composedFields.forEach(cf => {
            result[cf.fieldName] = buildComposedField(row, cf);
        });
    }

    return result;
});

// Load
const outputJson = output.map(item => ({ json: item }));

console.log(outputJson);