const env = process.env.NODE_ENV || 'development';
const config = require('../config/config')[env];
let All_Models = require('../models/all_models');

const Sequelize = require('sequelize');
const Op = Sequelize.Op;
let constants = require('../config/constants');
let moment = require('moment');
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

exports.toggle_scheduler = function (req, res) {
  sequelize.query("select * from app_settings where [app_settings].[name] = 'stop_all_mft_schedules'", {type: sequelize.QueryTypes.SELECT}).then(mft_scheduler => {
    console.log(mft_scheduler);
    sql = "update app_settings set value = 'false' where [app_settings].[name] = 'stop_all_mft_schedules' and env = '"+config.env+"'"
    if(mft_scheduler[0].value.toLowerCase() === 'false')
    {
      sql = "update app_settings set value = 'true' where [app_settings].[name] = 'stop_all_mft_schedules' and env = '"+config.env+"'"
    }
    sequelize.query(sql, {type: sequelize.QueryTypes.SELECT}).then(mft_scheduler => {
      res.redirect('/mft_schedules/');
    });
  });
}

exports.index = function (req, res) {
  //console.log('JSD referer: '+ req.headers.referer);
  var where = {};
  for (const qk in req.query){
    for (const key in All_Models.MFT_Schedule.rawAttributes) {
      if (qk === key) {
        where[key] = req.query[qk]
      }
    }
  }
  All_Models.MFT_Schedule.findAll({
    where: where,
    order: [['id','DESC']],
    include: [{
      model: All_Models.Endpoint,
      as: 'Endpoint',
      //where: { producer_id: Sequelize.col('endpoint.id')}
    }]
  }).then(function (mft_schedules) {
    sequelize.query("select * from app_settings where [app_settings].[name] = 'stop_all_mft_schedules'", {type: sequelize.QueryTypes.SELECT}).then(mft_scheduler => {
      //console.log(mft_scheduler);
      let sched_status = 'ON';
      if(mft_scheduler[0].value.toLowerCase() === 'true')
      {
        sched_status = 'OFF';
      }
      //console.log(where['active']);
      //hack around sequelize stupid datetime behavior
      for (let m=0; m < mft_schedules.length; m++){
        mft_schedules[m] = mft_schedules[m].setValuesForDisplay();
      }
      res.render('mft_schedule', {
        mft_schedules: mft_schedules,
        dateformat: require('dateformat'),
        wparms: where,
        sched_status: sched_status,
        moment: moment,
        error_message: req.flash('error_message'),
        success_message: req.flash('success_message'),
        frequency_types: constants.mft_freq_types,
      });
    });
    
  });
};

exports.get_create = function (req, res) {
  All_Models.Endpoint.findAll({
    //mft schedules should only use mft endpoints that are producers
    where: {
      type: {
        [Op.like]:'MFT%'
      },
      direction: 'producer',
      
    },
    order: [['bw_process_ident', 'ASC']]
  }).then(function (endpoints) {
    let redirect = '/mft_schedules';
    if(req.query.endpoint_id){ redirect = '/endpoints/view?' }
    res.render('mft_schedule_add', {
      redirect: redirect,
      endpoint_id: req.query.endpoint_id || 0,
      endpoints: endpoints,
      error_message: req.flash('error_message'),
      frequency_types: constants.mft_freq_types,
      sub_day_frequency_types: constants.mft_sub_day_freq_types,
      dateformat: require('dateformat'),
      weekdays: constants.weekdays,
      monthly_weekly_options: constants.monthly_weekly_options,
    });
  });
};

exports.post_create = function (req, res) {
  //console.log(req.body);
  //fix checkbox to boolean
  req.body.active = (req.body.active === 'on') ? 1 : 0;
  req.body.sub_day_stop_schedule = (req.body.sub_day_stop_schedule === 'on') ? 1 : 0;
  //logic for which field to pull interval from
  let freq_type = req.body.freq_type;
  //console.log(freq_type);
  //console.log(req.body.spec_date);
  //console.log(req.body.spec_time);
  let fmt = 'YYYY-MM-DD HH:mm:ss';
  if(req.body.pause_start && req.body.pause_end){
    //lets auto put date, we don't need it so we will do now
    req.body.pause_start = moment().format('YYYY-MM-DD')+' '+req.body.pause_start+':00';
    req.body.pause_end = moment().format('YYYY-MM-DD')+' '+req.body.pause_end+':00';
    //console.log(req.body.pause_start);
    //console.log(req.body.pause_end);
    let pause_start = moment(req.body.pause_start);//.utcOffset(-7);//.format(fmt);
    let pause_end = moment(req.body.pause_end);//.utcOffset(-7);//.format(fmt);
    //console.log(pause_start);
    //console.log(pause_end);
    req.body.pause_start = pause_start;
    req.body.pause_end = pause_end;
  }
  else {
    req.body.pause_start = null;
    req.body.pause_end = null;
  }
  let bulkSchedArray = [];
  switch (freq_type) {

    case "Specific_Date_and_Time":
      //freq_interval doesn't matter but we need the spec_date, spec_time fields
      if (req.body.spec_date === null || req.body.spec_date === "null" || req.body.spec_date.length < 1){
        req.flash('error_message', 'Selecting specific date and time frequency type requires entering a specific date!');
        return res.redirect('/mft_schedules/add');
      }
      if (req.body.spec_time === null || req.body.spec_time === "null" || req.body.spec_time.length < 1){
        req.flash('error_message', 'Selecting specific date and time frequency type requires entering a specific time!');
        return res.redirect('/mft_schedules/add');
      }
      
      break;
    case "Specific_Time_Daily":
      if (req.body.spec_time === null || req.body.spec_time === "null" || req.body.spec_time.length < 1){
        req.flash('error_message', 'Selecting specific time daily as frequency type requires entering a specific time!');
        return res.redirect('/mft_schedules/add');
      }
      req.body.spec_date = null;
      break;
    case "Minutes":
      if (req.body.freq_interval_minutes === null || req.body.freq_interval_minutes === "null" || req.body.freq_interval_minutes.length < 1){
        req.flash('error_message', 'Selecting Minutes as frequency type requires entering a Frequency Interval in Minutes value!');
        return res.redirect('/mft_schedules/add');
      }
      req.body.freq_interval = req.body.freq_interval_minutes;
      req.body.spec_time = null;
      req.body.spec_date = null;
      break;
    case "Hours":
      if (req.body.freq_interval_hours === null || req.body.freq_interval_hours === "null" || req.body.freq_interval_hours.length < 1){
        req.flash('error_message', 'Selecting Hours as frequency type requires entering a Frequency Interval in Hours value!');
        return res.redirect('/mft_schedules/add');
      }
      req.body.freq_interval = req.body.freq_interval_hours;
      req.body.spec_time = null;
      req.body.spec_date = null;
      break;
    case "Daily":
      if (req.body.freq_interval_days === null || req.body.freq_interval_days === "null" || req.body.freq_interval_days.length < 1){
        req.flash('error_message', 'Selecting Daily as frequency type requires entering a Frequency Interval in Days value!');
        return res.redirect('/mft_schedules/add');
      }
      req.body.freq_interval = req.body.freq_interval_days;
      req.body.spec_date = null;
      break;
    case "Multi Times a Day":
      if (req.body.freq_interval_days === null || req.body.freq_interval_days === "null" || req.body.freq_interval_days.length < 1){
        req.flash('error_message', 'Selecting Daily as frequency type requires entering a Frequency Interval in Days value!');
        return res.redirect('/mft_schedules/add');
      }
      req.body.freq_interval = req.body.freq_interval_days;
      req.body.spec_date = null;
      //get how many daily times
      let count = req.body.multi_time_count;
      //make a that many dailies
      for(let i=0; i<count;i++){
        bulkSchedArray.push({
          endpoint_id: req.body.endpoint_id,
          name: req.body.name,
          active: req.body.active,
          freq_type: 'Daily',
          freq_interval: req.body.freq_interval_days,
          spec_time: req.body['spec_time_'+(i+1)],
          spec_date: null,
          pause_start: req.body.pause_start,
          pause_end: req.body.pause_end
        });
      }
      //get each time for that count
      break;
    case "Weekly":
      if (req.body.freq_interval_weekly === null || req.body.freq_interval_weekly === "null" || req.body.freq_interval_weekly.length < 1){
        req.flash('error_message', 'Selecting Weekly as frequency type requires entering a Frequency Interval (Weekly) value!');
        return res.redirect('/mft_schedules/add');
      }
      req.body.freq_interval = req.body.freq_interval_weekly;
      req.body.spec_date = null;
      break;
    case "Multi Day Of Week":
      console.log(req.body.multi_freq_interval_weekly)
      if (req.body.multi_freq_interval_weekly === null || req.body.multi_freq_interval_weekly === "null" || req.body.multi_freq_interval_weekly.length < 1){
        req.flash('error_message', 'Selecting Weekly as frequency type requires entering a Frequency Interval (Weekly) value!');
        return res.redirect('/mft_schedules/add');
      }
      //we got what we need to make multiple schedules
      
      if(typeof(req.body.multi_freq_interval_weekly) === 'string'){
        //fix when bulk add was used for a single
        req.body.multi_freq_interval_weekly = [req.body.multi_freq_interval_weekly];
      }
      for(let i=0; i<req.body.multi_freq_interval_weekly.length;i++){
        bulkSchedArray.push({
          endpoint_id: req.body.endpoint_id,
          name: req.body.name,
          active: req.body.active,
          freq_type: 'Weekly',
          freq_interval: req.body.multi_freq_interval_weekly[i],
          spec_time: req.body.spec_time,
          spec_date: null,
          pause_start: req.body.pause_start,
          pause_end: req.body.pause_end
        });
      }
      
      req.body.spec_date = null;
      break;
    case "Monthly":
      if (req.body.freq_interval_monthly === null || req.body.freq_interval_monthly === "null" || req.body.freq_interval_monthly.length < 1){
        req.flash('error_message', 'Selecting Monthly as frequency type requires entering a Frequency Interval (Monthly) value!');
        return res.redirect('/mft_schedules/add');
      }
      req.body.freq_interval = req.body.freq_interval_monthly;
      req.body.spec_date = null;
      break;
    case "Monthly_Weekly":
      //console.log(req.body.spec_time);
      req.body.freq_interval = req.body.freq_interval_monthly_weekly;
      req.body.sub_freq_interval = req.body.sub_freq_interval_monthly_weekly;
      if(req.body.spec_time.length < 1){
        req.body.spec_time = null;
      }
      req.body.spec_date = null;
      break;
    case "Yearly":
      if (req.body.spec_date === null || req.body.spec_date === "null" || req.body.spec_date.length < 1){
        req.flash('error_message', 'Selecting yearly requires entering a specific date (year is ignored)!');
        return res.redirect('/mft_schedules/add');
      }
      if(req.body.sub_day_freq_interval === 'None'){
        if (req.body.spec_time === null || req.body.spec_time === "null" || req.body.spec_time.length < 1){
          req.flash('error_message', 'Selecting yearly requires entering a specific time!');
          return res.redirect('/mft_schedules/add');
        }
      }
      
      req.body.freq_interval = 0;
      break;
    default:
      return res.redirect('/mft_schedules/');
  }
  switch (req.body.sub_day_freq_type) {
    case "None":
      req.body.sub_day_freq_interval = null;
      req.body.sub_day_stop_schedule = null;
      req.body.sub_day_start_time = null;
      req.body.sub_day_end_time = null;
      /*if(req.body.freq_type === 'Daily' || req.body.freq_type === 'Weekly' || req.body.freq_type === 'Monthly'){
        req.body.spec_time = null;
      }*/
      break;
    case "Minutes":
      req.body.sub_day_freq_interval = req.body.sub_day_freq_interval_minutes;
      req.body.spec_time = null;
      if(req.body.sub_day_start_time.length < 1 || req.body.sub_day_end_time.length < 1){
        req.body.sub_day_start_time = null;
        req.body.sub_day_end_time = null;
      }
      break;
    case "Hours":
      req.body.sub_day_freq_interval = req.body.sub_day_freq_interval_hours;
      req.body.spec_time = null;
      if(req.body.sub_day_start_time.length < 1 || req.body.sub_day_end_time.length < 1){
        req.body.sub_day_start_time = null;
        req.body.sub_day_end_time = null;
      }
      break;
    case "Specific_Time":
      req.body.sub_day_freq_interval = null;
      req.body.sub_day_stop_schedule = null;
      req.body.sub_day_start_time = null;
      req.body.sub_day_end_time = null;
      break;
  }
  //lets add the sub day info to the multi weekly if that is what was submitted
  if(freq_type === "Multi Day Of Week" || freq_type === "Multi Times a Day"){  
    if(freq_type === "Multi Day Of Week"){
      //lets pull in subday config for each and save each
      for(let s=0;s<bulkSchedArray.length;s++){
        bulkSchedArray[s].sub_day_freq_type = req.body.sub_day_freq_type;
        bulkSchedArray[s].sub_day_freq_interval = req.body.sub_day_freq_interval;
        //reassign spec time in case sub day reset it
        bulkSchedArray[s].spec_time = req.body.spec_time
        bulkSchedArray[s].sub_day_stop_schedule = req.body.sub_day_stop_schedule;
        bulkSchedArray[s].sub_day_start_time = req.body.sub_day_start_time;
        bulkSchedArray[s].sub_day_end_time = req.body.sub_day_end_time;
      }
    }
    All_Models.MFT_Schedule.bulkCreate(bulkSchedArray).then(() => {
      if(req.body.redirect.includes('/mft_schedules')){
        return res.redirect('/mft_schedules');
      }
      res.redirect('/endpoints/view?id='+req.body.endpoint_id);
    })
  }
  else{
    All_Models.MFT_Schedule.create(req.body).then(mft_schedule => {
      if(req.body.redirect.includes('/mft_schedules')){
        return res.redirect('/mft_schedules');
      }
      res.redirect('/endpoints/view?id='+mft_schedule.endpoint_id);
    });
  }
  
};

exports.get_view = function (req, res) {
  All_Models.MFT_Schedule.findByPk(req.query.id, {
    include: [{
      model: All_Models.Endpoint,
      as: 'Endpoint',
      //where: { producer_id: Sequelize.col('endpoint.id')}
    }]
  }).then(function (mft_schedule) {
    res.render('mft_schedule_view', {
      mft_schedule: mft_schedule,
      dateformat: require('dateformat')
    });

  })
};

exports.get_edit = function (req, res) {
  const df = require('dateformat');
  All_Models.MFT_Schedule.findByPk(req.query.id, {
    include: [{
      model: All_Models.Endpoint,
      as: 'Endpoint',
      //where: { producer_id: Sequelize.col('endpoint.id')}
    }]
  }).then(function (mft_schedule) {
    //console.log(mft_schedule);
    All_Models.Endpoint.findAll({
      //mft schedules should only use mft endpoints that are producers
      where: {
        type: {
          [Op.like]:'MFT%'
        },
        direction: 'producer',
        
      },
      order: [['bw_process_ident', 'ASC']]
    }).then(function (endpoints) {
      //console.log(endpoints);
      //most need moment.utc to fix an auto shift that node/sequelize/moment does since we don't do DATETIMEOFFSET in mssql
      //but only the full datetime's do we reset format in controller otherwise we do in view with dateformat function
      if(mft_schedule.spec_date){
        //console.log(mft_schedule.spec_date);
        mft_schedule.spec_date = moment.utc(mft_schedule.spec_date).format('YYYY-MM-DD');
      }
      if(mft_schedule.spec_time){
        mft_schedule.spec_time = moment.utc(mft_schedule.spec_time).format('HH:mm');
      }
      if(mft_schedule.sub_day_start_time){
        mft_schedule.sub_day_start_time = moment.utc(mft_schedule.sub_day_start_time).format('HH:mm');
        //  console.log(mft_schedule.sub_day_start_time);
      }
      if(mft_schedule.sub_day_end_time){
        mft_schedule.sub_day_end_time = moment.utc(mft_schedule.sub_day_end_time).format('HH:mm');
      }
      if(mft_schedule.pause_start){
        //console.log(typeof mft_schedule.pause_start);
        mft_schedule.pause_start = moment.utc(mft_schedule.pause_start).format('YYYY-MM-DD[T]HH:mm');
      }
      if(mft_schedule.pause_end){
        mft_schedule.pause_end = moment.utc(mft_schedule.pause_end).format('YYYY-MM-DD[T]HH:mm');
      }
      let redirect = '/endpoints/view?';
      if(req.headers.referer.includes('/mft_schedules')){
        redirect = '/mft_schedules';
      }
      res.render('mft_schedule_edit', {
        redirect: redirect,
        mft_schedule: mft_schedule,
        endpoints: endpoints,
        error_message: req.flash('error_message'),
        frequency_types: constants.mft_freq_types,
        sub_day_frequency_types: constants.mft_sub_day_freq_types,
        dateformat: require('dateformat'),
        weekdays: constants.weekdays,
        monthly_weekly_options: constants.monthly_weekly_options,
      });
    });
  })
};

exports.post_edit = function (req, res){
  //console.log(req.body);
  All_Models.MFT_Schedule.findByPk(req.body.id).then(function (mft_schedule) {
    
    //fix checkbox to boolean
    req.body.active = (req.body.active === 'on') ? 1 : 0;
    req.body.sub_day_stop_schedule = (req.body.sub_day_stop_schedule === 'on') ? 1 : 0;
    
    let fmt = 'YYYY-MM-DD HH:mm:ss';
    if(req.body.pause_start && req.body.pause_end){
      //lets auto put date, we don't need it so we will do now
      req.body.pause_start = moment().format('YYYY-MM-DD')+' '+req.body.pause_start+':00';
      req.body.pause_end = moment().format('YYYY-MM-DD')+' '+req.body.pause_end+':00';
      //console.log(req.body.pause_start);
      //console.log(req.body.pause_end);
      let pause_start = moment(req.body.pause_start).format(fmt);
      let pause_end = moment(req.body.pause_end).format(fmt);
      //console.log(pause_start);
      //console.log(pause_end);
      req.body.pause_start = pause_start;
      req.body.pause_end = pause_end;
    }
    else {
      req.body.pause_start = null;
      req.body.pause_end = null;
    }
    
    //adjust for freq_type
    switch (req.body.freq_type) {

      case "Specific_Date_and_Time":
        req.body.freq_interval = 0;
        break;
      case "Specific_Time_Daily":
        req.body.spec_date = null;
        break;
      case "Minutes":
        req.body.freq_interval = req.body.freq_interval_minutes;
        req.body.spec_time = null;
        req.body.spec_date = null;
        break;
      case "Hours":
        req.body.freq_interval = req.body.freq_interval_hours;
        req.body.spec_time = null;
        req.body.spec_date = null;
        break;
      case "Daily":
        req.body.freq_interval = req.body.freq_interval_days;
        if(req.body.spec_time.length < 1){
          req.body.spec_time = null;
        }
        req.body.spec_date = null;
        break;
      case "Weekly":
        req.body.freq_interval = req.body.freq_interval_weekly;
        if(req.body.spec_time.length < 1){
          req.body.spec_time = null;
        }
        req.body.spec_date = null;
        break;
      case "Monthly":
        //console.log(req.body.spec_time);
        req.body.freq_interval = req.body.freq_interval_monthly;
        if(req.body.spec_time.length < 1){ 
          req.body.spec_time = null;
        }
        req.body.spec_date = null;
        break;
      case "Monthly_Weekly":
        //console.log(req.body.spec_time);
        req.body.freq_interval = req.body.freq_interval_monthly_weekly;
        req.body.sub_freq_interval = req.body.sub_freq_interval_monthly_weekly;
        if(req.body.spec_time.length < 1){
          req.body.spec_time = null;
        }
        req.body.spec_date = null;
        break;
      case "Yearly":
        req.body.freq_interval = 0;
        if (req.body.spec_date === null || req.body.spec_date === "null" || req.body.spec_date.length < 1){
          req.flash('error_message', 'Selecting yearly requires entering a specific date (year is ignored) and time!');
          return res.redirect('/mft_schedules/edit?id='+mft_schedule.id);
        }
        if(req.body.sub_day_freq_interval === 'None'){
          if (req.body.spec_time === null || req.body.spec_time === "null" || req.body.spec_time.length < 1){
            req.flash('error_message', 'Selecting yearly requires entering a specific time!');
            return res.redirect('/mft_schedules/edit?id='+mft_schedule.id);
          }
        }
        break;
      default:
        //nothing
    }
    switch (req.body.sub_day_freq_type) {
      case "None":
        req.body.sub_day_freq_interval = null;
        req.body.sub_day_stop_schedule = null;
        req.body.sub_day_start_time = null;
        req.body.sub_day_end_time = null;
        /*
        This is opposite what we want now, we require these and yearly to have a spec time if no sub day
        if(req.body.freq_type === 'Daily' || req.body.freq_type === 'Weekly' || req.body.freq_type === 'Monthly'){
          req.body.spec_time = null;
        }*/
        
        break;
      case "Minutes":
        req.body.sub_day_freq_interval = req.body.sub_day_freq_interval_minutes;
        req.body.spec_time = null;
        if(req.body.sub_day_start_time.length < 1 || req.body.sub_day_end_time.length < 1){
          req.body.sub_day_start_time = null;
          req.body.sub_day_end_time = null;
        }
        break;
      case "Hours":
        req.body.sub_day_freq_interval = req.body.sub_day_freq_interval_hours;
        req.body.spec_time = null;
        if(req.body.sub_day_start_time.length < 1 || req.body.sub_day_end_time.length < 1){
          req.body.sub_day_start_time = null;
          req.body.sub_day_end_time = null;
        }
        break;
      case "Specific_Time":
        req.body.sub_day_freq_interval = null;
        req.body.sub_day_stop_schedule = null;
        req.body.sub_day_start_time = null;
        req.body.sub_day_end_time = null;
        break;
    }
    //console.log(req.body);
    if (req.body.reset_last_run) {
        req.body.last_run = moment('1969-07-20 00:03:17').format(fmt)
    }
    mft_schedule.update(req.body).then(function (mft_schedule) {
      if(req.body.redirect.includes('/mft_schedules')){
        return res.redirect('/mft_schedules');
      }
      res.redirect('/endpoints/view?id='+mft_schedule.endpoint_id);
    });
  });
};

exports.get_remove = function (req, res) {
  //console.log('JSD referer: '+ req.headers.referer);
  All_Models.MFT_Schedule.findByPk(req.query.id, {}).then(function (mft_schedule) {
    //let endpoint_id = endpoint_prop.endpoint_id;
    mft_schedule.destroy().then(mft_schedule => {
      req.flash('success_message', 'Schedule Deleted!');
      if(req.headers.referer.includes('/mft_schedules')){
        return res.redirect('/mft_schedules');
      }
      res.redirect('/endpoints/view?id='+mft_schedule.endpoint_id);
    })
  });
};
