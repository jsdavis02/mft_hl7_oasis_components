const env = process.env.NODE_ENV || 'development';
const config = require('../config/config')[env];
//var Code_Table = require('../models/code_table');
//const csv = require('csvtojson');
const Sequelize = require('sequelize');
const sequelize = new Sequelize(config.database.db,config.database.user,config.database.pass, {
  host: config.database.host,
  dialect: 'mssql',
  operatorsAliases: false,

  pool: {
    max: 5,
    min: 0,
    acquire: 30000,
    idle: 10000
  },
});

exports.admin_dash = function (req, res) {
  sequelize.query('select count(*) as all_e from endpoints', {type: sequelize.QueryTypes.SELECT}).then(e_count => {
    sequelize.query('select count(*) as active_e from endpoints where active = 1', {type: sequelize.QueryTypes.SELECT}).then(ae_count => {
      sequelize.query('select count(*) as hl7_e from endpoints where type = \'HL7\'', {type: sequelize.QueryTypes.SELECT}).then(he_count => {
        sequelize.query('select count(*) as fs_e from endpoints where type = \'MFT-FS\'', {type: sequelize.QueryTypes.SELECT}).then(fse_count => {
          sequelize.query('select count(*) as sftpc_e from endpoints where type = \'MFT-SFTP-Client\'', {type: sequelize.QueryTypes.SELECT}).then(sftpce_count => {
            sequelize.query('select count(*) as smbc_e from endpoints where type = \'MFT-SMB\'', {type: sequelize.QueryTypes.SELECT}).then(smbce_count => {
              sequelize.query('select count(*) as all_r from routes', {type: sequelize.QueryTypes.SELECT}).then(r_count => {
                sequelize.query('select count(*) as active_r from routes where active = 1', {type: sequelize.QueryTypes.SELECT}).then(ar_count => {
                  sequelize.query('select count(*) as h_r from routes where type = \'HL7\'', {type: sequelize.QueryTypes.SELECT}).then(hr_count => {
                    sequelize.query('select count(*) as m_r from routes where type = \'MFT\'', {type: sequelize.QueryTypes.SELECT}).then(mr_count => {
                      sequelize.query('select count(*) as hw_a from audit where ProcessState = \'received\' and proc_time >= dateadd(day, -7, getdate());', {type: sequelize.QueryTypes.SELECT}).then(hl7_week_received => {
                        sequelize.query('select count(*) as fsw_a from audit where ProcessState = \'mft-fs-check-has-files\' and proc_time >= dateadd(day, -7, getdate());', {type: sequelize.QueryTypes.SELECT}).then(fs_week_received => {
                          sequelize.query('select count(*) as sftpcw_a from audit where ProcessState = \'mft-sftp-check-has-files\' and proc_time >= dateadd(day, -7, getdate());', {type: sequelize.QueryTypes.SELECT}).then(sftpce_week_received => {
                            sequelize.query('select count(*) as sftpcd_a from audit where ProcessState = \'mft-sftp-check-has-files\' and proc_time >= dateadd(day, -1, getdate());', {type: sequelize.QueryTypes.SELECT}).then(sftpce_day_received => {
                              sequelize.query('select count(*) as a_cnt from audit', {type: sequelize.QueryTypes.SELECT}).then(all_audit_count => {
                                res.render('admin_dash_home', {
                                  e_count: e_count[0].all_e,
                                  ae_count: ae_count[0].active_e,
                                  he_count: he_count[0].hl7_e,
                                  fse_count: fse_count[0].fs_e,
                                  sftpce_count: sftpce_count[0].sftpc_e,
                                  smbce_count: smbce_count[0].smbc_e,
                                  r_count: r_count[0].all_r,
                                  ar_count: ar_count[0].active_r,
                                  hr_count: hr_count[0].h_r,
                                  mr_count: mr_count[0].m_r,
                                  hl7_week_received: hl7_week_received[0].hw_a,
                                  fs_week_received: fs_week_received[0].fsw_a,
                                  sftpce_week_received: sftpce_week_received[0].sftpcw_a,
                                  sftpce_day_received: sftpce_day_received[0].sftpcd_a,
                                  audit_count_total: all_audit_count[0].a_cnt
                                });
                              });
                            });
                          });
                        });
                      });
                    });
                  });
                });
              });
            });
          });
        });
      });
    });
  });
  
};

exports.analyst_dash = function (req, res) {
  res.render('analyst_dash_home', {

  });
};

