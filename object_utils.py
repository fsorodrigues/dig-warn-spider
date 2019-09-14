# import datetime module
from datetime import datetime

# function wraps creation of dict object
def create_employer_object(notice,employer_id,timestamp):
    obj = {
        "employer_name":notice["employer_name"],
        "employer_id":employer_id,
        "date_created":timestamp,
        "notices":[int(notice["notice_id"])],
    }

    return obj

# function wraps creation of dict object
def create_notice_object(notice,detailed_data,employer_id,timestamp):
    obj = {
        "notice_id":int(notice["notice_id"]),
        "notice_date":datetime.strptime(notice["notice_date"],"%m/%d/%Y").isoformat(),
        "employer_id":employer_id,
        "date_created":timestamp,
        "url":notice["notice_url"],
        "total_affected":int(detailed_data["total_affected"]),
        "address": {
            "street_address":detailed_data["street_address"],
            "city":detailed_data["city"],
            "state":detailed_data["state"],
            "zip":notice["zip"],
            "lwib_area":notice["lwib_area"]
        }
    }

    return obj
