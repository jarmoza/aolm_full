metadata_info = {

	# "path": "/Users/PeregrinePickle/htrc_data_files/nyp_ef_files_compressed/",
	"path": "/Users/PeregrinePickle/Documents/Digital_Humanities/htrc_playground/data/ninec_tests/nyp_sandbox/test_subset/",

	"data_types": {

		"schema": {
			"accessProfile": ["str"],
			"bibliographicFormat": ["str"],
			"classification": ["str", "dict"],
			"dateCreated": ["str", "datetime"],
			"enumerationChronology": ["str"],
			"genre": ["str", "list"],
			"governmentDocument": ["bool"],
			"handleUrl": ["str", "unique_uri"],
			"hathitrustRecordNumber": ["str", "unique_id"],
			"htBibUrl": ["str", "unique_uri"],
		    "imprint": ["str"],
		    "isbn": ["str", "list", "unique_id"],
		    "issn": ["str", "list", "unique_id"],
		    "issuance": ["str"],
		    "language": ["str"],
		    "lastUpdateDate": ["str", "datetime"],
		    "lccn": ["str", "list", "unique_id"],
		    "names": ["str", "list"],
		    "oclc": ["str", "list", "unique_id"],
		    "pubDate": ["str", "datetime", "year"],
			"schemaVersion": ["str", "fl_num_range"],
		    "sourceInstitution": ["str"],
		    "sourceInstitutionRecordNumber": ["str", "unique_id"],
			"title": ["str"],
			"typeOfResource": ["str"],
			"volumeIdentifier": ["str", "unique_id"]   
		}	

	},

	"expectations": {

		"schema": {
			"accessProfile": [],
			"bibliographicFormat": [],
			"classification": [],
			"dateCreated": [],
			"enumerationChronology": [],
			"genre": [],
			"governmentDocument": [],
			"handleUrl": [],
			"hathitrustRecordNumber": [],
			"htBibUrl": [],
		    "imprint": [],
		    "isbn": [],
		    "issn": [],
		    "issuance": [],
		    "language": [],
		    "lastUpdateDate": [],
		    "lccn": [],
		    "names": [],
		    "oclc": [],
		    "pubDate": [],
			"schemaVersion": [],
		    "sourceInstitution": [],
		    "sourceInstitutionRecordNumber": [],
			"title": [],
			"typeOfResource": [],
			"volumeIdentifier": []   
		}

	}

}

metadata_expectation_info = {
	

}

# metadata_info = {
	
# 	"path": "/Users/PeregrinePickle/htrc_data_files/nyp_ef_files_compressed/",
# 	"schema": {
# 		"schemaVersion": ["str", "fl_num_range"],
# 		"dateCreated": ["str", "datetime"],
# 		"volumeIdentifier": ["str", "unique_id"],
# 		"accessProfile": ["str"],
# 	    "hathitrustRecordNumber": ["str", "unique_id"],
# 	    "enumerationChronology": ["str"],
# 	    "sourceInstitution": ["str"],
# 	    "sourceInstitutionRecordNumber": ["str", "unique_id"],
# 	    "oclc": ["str", "list", "unique_id"],
# 	    "isbn": ["str", "list", "unique_id"],
# 	    "issn": ["str", "list", "unique_id"],
# 	    "lccn": ["str", "list", "unique_id"],
# 	    "title": ["str"],
# 	    "imprint": ["str"],
# 	    "lastUpdateDate": ["str", "datetime"],
# 	    "governmentDocument": ["bool"],
# 	    "pubDate": ["str", "datetime", "year"],
# 	    "pubPlace": ["str"],
# 	    "language": ["str"],
# 	    "bibliographicFormat": ["str"],
# 	    "genre": ["str", "list"],
# 	    "issuance": ["str"],
# 	    "typeOfResource": ["str"],
# 	    "classification": ["str", "dict"],
# 	    "names": ["str", "list"],
# 	    "htBibUrl": ["str", "unique_uri"],
# 	    "handleUrl": ["str", "unique_uri"],
# 	}
# }

