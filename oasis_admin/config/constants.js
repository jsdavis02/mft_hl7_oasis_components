const endpoint_types = ['MFT-FS', 'MFT-SMB', 'MFT-SFTP-Client', 'MFT-MSTR-Scheduler'];
const request_types = [
  {type: 'MFT-FS', label: 'In Hospital Network File Location'},
  {type: 'MFT-SMB', label: 'In Hospital Windows File Location'},
  {type: 'MFT-SFTP-Client', label: 'In or Out of Hospital SFTP Location'},
  // {type: 'HL7', label: 'Real Time HL7'},
  {type: 'unknown', label: 'Do Not Know'}];
const weekdays = [
  {value: 1, label: 'Sunday'}, 
  {value: 2, label: 'Monday'},
  {value: 3, label: 'Tuesday'},
  {value: 4, label: 'Wednesday'},
  {value: 5, label: 'Thursday'},
  {value: 6, label: 'Friday'},
  {value: 7, label: 'Saturday'}
];
const monthly_weekly_options = [
  {value: 1, label: 'First'},
  {value: 2, label: 'Second'},
  {value: 3, label: 'Third'},
  {value: 4, label: 'Fourth'},
  {value: 5, label: 'Fifth'},
  {value: -1, label: 'Last'},
];
const alert_levels = [
  {value: 1, label: 'CRITICAL'},
  {value: 2, label: 'HIGH'},
  {value: 3, label: 'MEDIUM'},
  {value: 4, label: 'LOW'},
  {value: 100, label: 'NONE'}
];
// const messagetypes = ['ADT', 'MDM', 'ORD', 'ORM'];
// const triggerevents = ['ADT.A01', 'ADT.A02', 'ADT.A03', 'ADT.A04', 'ADT.A05', 'ADT.A06', 'ADT.A07', 'ADT.A08', 'ADT.A09', 'ADT.A10', 'ADT.A11','ADT.A12', 'ADT.A13', 'ADT.A14', 'ADT.A15', 'ADT.A16', 'ADT.A17', 'ADT.A18', 'ADT.A19', 'ADT.A20', 'ADT.A21', 'ADT.A22', 'ADT.A23', 'ADT.A24', 'ADT.A25',
//   'ADT.A26', 'ADT.A27', 'ADT.A28', 'ADT.A29', 'ADT.A30', 'ADT.A31', 'ADT.A32', 'ADT.A33', 'ADT.A34', 'ADT.A35', 'ADT.A36', 'ADT.A37', 'ADT.A38', 'ADT.A39',
//   'ADT.A40', 'ADT.A41', 'ADT.A42', 'ADT.A43', 'ADT.A44', 'ADT.A45', 'ADT.A46', 'ADT.A47', 'ADT.A48', 'ADT.A49', 'ADT.A50', 'ADT.A51', 'ADT.A52', 'ADT.A53',
//   'ADT.A54', 'ADT.A55', 'ADT.A56', 'ADT.A60', 'ADT.A61', 'ADT.A62', 'MDM.T01', 'MDM.T02', 'MDM.T03', 'MDM.T04', 'MDM.T05', 'MDM.T06', 'MDM.T07', 'MDM.T08', 'MDM.T09', 'MDM.T10', 'MDM.T11',
//   'DFT.P03', 'ORM.O01', 'ORU.R01', 'ORU.R30', 'ORU.R31', 'ORU.R32', 'ORR.O01', 'ORR.O02', 'MFT.FS', 'MFT.SMB', 'MFT.SFTP'];
const triggerevents = ['MFT.FS', 'MFT.SMB', 'MFT.SFTP'];
const route_types = ['MFT'];
const env_list = ['PRD', 'PPRD', 'TST', 'DEV', 'STG'];
const mft_freq_types = ['Specific_Date_and_Time', 'Minutes', 'Hours', 'Daily', 'Weekly', 'Monthly', 'Monthly_Weekly', 'Yearly', 'Multi Day Of Week', 'Multi Times a Day', 'Trigger'];
const mft_sub_day_freq_types = ['None', 'Minutes', 'Hours'];
const endpoint_propnames = {
  // 'HL7': {
  //   'consumer_host': 'Consumer fully qualified domain name or IP',
  //   'consumer_port': 'Consumer port number',
  //   'send_retry_sleep': 'Retry sleep in milliseconds',
  //   'send_retry_max': 'Max number of retry attempts',
  //   'producer_host': 'Producer fully qualified domain name or IP',
  //   'producer_port': 'Producer port number'
  // },
  'MFT-FS': {
    'fs_path': 'Filesystem path',
    'fs_file_filter': 'Python script to do complex file filtering on Producer file pickups',
    'filename_pattern': 'Description of filename pattern',
    'delete_fs_source': 'Delete FS source files',
    'audit_persist': 'Set true to archive the file data during audit logging',
    'destination_file_exists': 'Set action if source file exists at destination: overwrite(default), rename, skip, or error',
    'rename_behavior': 'Set to timestamp or increment to define how file is renamed',
    'endpoint_contact': 'Endpoint contact name',
    'endpoint_email': 'Endpoint contact email',
    'endpoint_phone': 'Endpoint contact phone',
    'confirm_notification_email': 'Successful file(s) transfer notification recipient',
    'nofiles_notification_email': 'No files found notification recipient',
    'error_notification_email': 'Additional email recipients if there is an error with this endpoint',
    'delete_only': 'Tells the engine the producer is just to pickup and remove files that fit the filter but do not route',
  },
  'MFT-SMB': {
    'smb_path': 'SMB Consumer path /folder/sub part after host and share //Server/Share/folder/sub',
    'smb_host': 'SMB Host //Server part in //Server/Share/folder/sub',
    'smb_share': 'SMB Share Share part in //Server/Share/folder/sub',
    'smb_domain': 'SMB User domain to authenticate with, usually HCS',
    'smb_username': 'SMB User to authenticate with, usually our service account',
    'smb_password': 'SMB Password for user to authenticate with',
    'smb_file_filter_1': 'Python function to do file filtering on Producer file pickups, all_files will be used if none specified _2,3 etc are supported too',
    'filename_pattern': 'Description of filename pattern',
    'smb_path_1': 'Producer filepath following //Server/Share for Producer Endpoint with corresponding smb_file_filter_1',
    'delete_smb_source': 'Delete SMB source files after pickup if set to value of true',
    'audit_persist': 'Set true to archive the file data during audit logging or false to not persist data (default is persist)',
    'destination_file_exists': 'Set action if source file exists at destination: overwrite(default), rename, skip, or error',
    'rename_behavior': 'Set to timestamp or increment to define how file is renamed',
    'endpoint_contact': 'Endpoint contact name',
    'endpoint_email': 'Endpoint contact email',
    'endpoint_phone': 'Endpoint contact phone',
    'confirm_notification_email': 'Successful file(s) transfer notification recipient',
    'nofiles_notification_email': 'No files found notification recipient',
    'error_notification_email': 'Additional email recipients if there is an error with this endpoint',
    'delete_only': 'Tells the engine the producer is just to pickup and remove files that fit the filter but do not route',
  },
  'MFT-SFTP-Client': {
    'sftp_host': 'SFTP fully qualified domain name or IP',
    'sftp_port': 'SFTP port',
    'sftp_username': 'SFTP username',
    'sftp_password': 'SFTP user password',
    'delete_sftp_source': 'Delete SFTP source files',
    'audit_persist': 'Set true to archive the file data during audit logging',
    'sftp_timeout': 'Set timeout value in seconds to override default',
    'sftp_key': 'SFTP public or private key filename',
    'sftp_key_password': 'SFTP key file password',
    'sftp_path': 'Consumer filepath destination relative to the sftp user home directory',
    'sftp_file_filter_1': 'Python script to do complex file filtering on Producer sftp gets of min is 1',
    'sftp_path_1': 'Producer filepath relative to user home directory for Producer Endpoint with corresponding sftp_file_filter_1',
    'filename_pattern': 'Description of filename pattern',
    'destination_file_exists': 'Set action if source file exists at destination: overwrite(default), rename, skip, or error',
    'rename_behavior': 'Set to timestamp or increment to define how file is renamed',
    'endpoint_contact': 'Endpoint contact name',
    'endpoint_email': 'Endpoint contact email',
    'endpoint_phone': 'Endpoint contact phone',
    'confirm_notification_email': 'Successful file(s) transfer notification recipient',
    'nofiles_notification_email': 'No files found notification recipient',
    'error_notification_email': 'Additional email recipients if there is an error with this endpoint',
    'put_confirm': 'Defaults to true if does not exist, but add and set to false to turn off Consumer sftp put trying to confirm file, useful for systems that immediately hide file after we put',
    'delete_only': 'Tells the engine the producer is just to pickup and remove files that fit the filter but do not route',
  },
  'MFT-MSTR-Scheduler': {
    'producer_id_1': 'Producer ID of first producer to invoke',
    'producer_id_2': 'Producer ID of second producer to invoke',
    'sleep_interval': 'Time in seconds between activity execution',
    'total_job_count': 'Number of producers',
    'no_files_ok_1': 'Proceed if no files are found by first producer',
    'no_files_ok_2': 'Proceed if no files are found by second producer',
    'pre-delay_1': 'Delay in seconds before first producer is invoked',
    'pre-delay_2': 'Delay in seconds before second producer is invoked',
    'post-delay_1': 'Delay in seconds after first producer completes',
    'post_delay_2': 'Delay in seconds after second producer completes',
    'get_response_1': 'Proceed only when first producer completes',
    'get_response_2': 'Proceed only when second producer completes',
    'wait_response_1': 'Time in seconds to wait for first producer to complete',
    'wait_response_2': 'Time in seconds to wait for second producer to complete'
  }
};

module.exports = {
  endpoint_types: endpoint_types,
  // messagetypes: messagetypes,
  triggerevents: triggerevents,
  route_types: route_types,
  mft_freq_types: mft_freq_types,
  mft_sub_day_freq_types: mft_sub_day_freq_types,
  endpoint_propnames: endpoint_propnames,
  env_list: env_list,
  request_types: request_types,
  weekdays: weekdays,
  monthly_weekly_options: monthly_weekly_options,
  alert_levels: alert_levels,
};