from django.conf import settings

WALLET = {
    "GEOLOCATIONS": {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "array",

        "items": {
            "type": "object",
            "minItems": 1,
            "maxItems": 10,
            "additionalProperties": False,

            "properties": {
                "longitude": {
                    "type": "number"
                },
                "latitude": {
                    "type": "number"
                },
                "message": {
                    "type": "string",
                    "minLength": 1
                }
            },

            "required": ["longitude", "latitude", "message"]
        }
    },

    "FRONTEND": {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",

        "properties": {
            "logo_text": {
                "type": "string",
                "minLength": 1
            },
            "background_color": {
                "type": "string",
                "pattern": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
            },
            "label_color": {
                "type": "string",
                "pattern": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
            },
            "foreground_color": {
                "type": "string",
                "pattern": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
            },
            "barcode_format": {
                "type": "string",
                "enum": settings.BARCODES
            },
            "is_show_the_number_card": {
                "type": "boolean"
            },
            "header_fields": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,

                    "properties": {
                        "key": {
                            "type": "string",
                            "minLength": 1
                        },
                        "value": {
                            "type": "string",
                            "minLength": 1
                        },
                        "label": {
                            "type": "string",
                            "minLength": 1
                        }
                    },

                    "required": ["key", "value", "label"]
                }
            },
            "primary_fields": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,

                    "properties": {
                        "key": {
                            "type": "string",
                            "minLength": 1
                        },
                        "value": {
                            "type": "string",
                            "minLength": 1
                        },
                        "label": {
                            "type": "string",
                            "minLength": 1
                        }
                    },

                    "required": ["key", "value", "label"]
                }
            },
            "secondary_fields": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,

                    "properties": {
                        "key": {
                            "type": "string",
                            "minLength": 1
                        },
                        "value": {
                            "type": "string",
                            "minLength": 1
                        },
                        "label": {
                            "type": "string",
                            "minLength": 1
                        }
                    },

                    "required": ["key", "value", "label"]
                }
            },
            "auxiliary_fields": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,

                    "properties": {
                        "key": {
                            "type": "string",
                            "minLength": 1
                        },
                        "value": {
                            "type": "string",
                            "minLength": 1
                        },
                        "label": {
                            "type": "string",
                            "minLength": 1
                        }
                    },

                    "required": ["key", "value", "label"]
                }
            }
        },

        "required": [
            "logo_text",
            "background_color",
            "label_color",
            "foreground_color",
            "barcode_format",
            "is_show_the_number_card"
        ]
    },

    "BACKEND": {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",

        "properties": {
            "push": {
                "type": "object",

                "properties": {
                    "title": {
                        "type": "string",
                        "minLength": 1
                    }
                },

                "required": ["title"]
            },
            "back_fields": {
                "type": "array",
                "minItems": 1,
                "maxItems": 5,
                "items": {
                    "type": "object",
                    "additionalProperties": False,

                    "properties": {
                        "key": {
                            "type": "string",
                            "minLength": 1
                        },
                        "value": {
                            "type": "string",
                            "minLength": 1
                        },
                        "label": {
                            "type": "string",
                            "minLength": 1
                        }
                    },

                    "required": ["key", "value", "label"]
                }
            },
            "associatedStoreIdentifiers": {
                "type": "array",
                "items": {
                    "type": "integer"
                }
            },
            "activation_message": {
                "type": "string",
                "minLength": 1
            },
            "sharingProhibited": {
                "type": "boolean"
            },
            "is_use_feedback_system": {
                "type": "boolean"
            }
        },

        "required": [
            "push",
            "back_fields",
            "activation_message",
            "sharingProhibited",
            "is_use_feedback_system"
        ]
    }
}
