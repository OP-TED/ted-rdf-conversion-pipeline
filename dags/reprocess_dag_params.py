from airflow.models import Param

from ted_sws.core.model.notice import NoticeStatus

FORM_NUMBER_DAG_PARAM = "form_number"
START_DATE_DAG_PARAM = "start_date"
END_DATE_DAG_PARAM = "end_date"
XSD_VERSION_DAG_PARAM = "xsd_version"

REPROCESS_DATE_RANGE_DAG_PARAMS = {
    START_DATE_DAG_PARAM: Param(
        default=None,
        type=["null", "string"],
        format="date",
        title="Start Date",
        description="""This field is optional. If you want to filter notices by start date, please insert a date.
        This field needs to be used with the end date field.
         """
    ),
    END_DATE_DAG_PARAM: Param(
        default=None,
        type=["null", "string"],
        format="date",
        title="End Date",
        description="""This field is optional. If you want to filter notices by end date, please insert a date.
         This field needs to be used with the start date field.
         """,
    )
}

REPROCESS_DAG_PARAMS = {
    FORM_NUMBER_DAG_PARAM: Param(
        default=None,
        type=["null", "string"],
        title="Form Number",
        description="This field is optional. If you want to filter notices by form number, please insert a form number."),
    **REPROCESS_DATE_RANGE_DAG_PARAMS,
    XSD_VERSION_DAG_PARAM: Param(
        default=None,
        type=["null", "string"],
        format="string",
        title="XSD Version",
        description="This field is optional. If you want to filter notices by XSD version, please insert a XSD version."
    )
}

RE_NORMALISE_TARGET_NOTICE_STATES = [NoticeStatus.RAW, NoticeStatus.INDEXED]

RE_TRANSFORM_TARGET_NOTICE_STATES = [NoticeStatus.NORMALISED_METADATA, NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION,
                                     NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION,
                                     NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION,
                                     NoticeStatus.TRANSFORMED, NoticeStatus.DISTILLED
                                     ]

RE_VALIDATE_TARGET_NOTICE_STATES = [NoticeStatus.DISTILLED]

RE_PACKAGE_TARGET_NOTICE_STATES = [NoticeStatus.VALIDATED, NoticeStatus.INELIGIBLE_FOR_PACKAGING,
                                   NoticeStatus.ELIGIBLE_FOR_PACKAGING,
                                   NoticeStatus.INELIGIBLE_FOR_PUBLISHING]

RE_PUBLISH_TARGET_NOTICE_STATES = [NoticeStatus.ELIGIBLE_FOR_PUBLISHING, NoticeStatus.INELIGIBLE_FOR_PUBLISHING,
                                   NoticeStatus.PACKAGED, NoticeStatus.PUBLICLY_UNAVAILABLE
                                   ]

RE_PROCESS_PUBLISHED_PUBLICLY_AVAILABLE_TARGET_NOTICE_STATES = [NoticeStatus.PUBLICLY_AVAILABLE]
