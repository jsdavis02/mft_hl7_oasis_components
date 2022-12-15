var config = {
    development: {
        //url to be used in link generation
        //url: 'http://my.site.com',
        //mongodb connection settings
        database: {
            host:   '127.0.0.1',
            //port:   '27017',
            db:     'site_dev',
            user: 'dbuser',
            pass: 'dbpass'
        },
        bw: {
            host: 'virps0esb20i03',
            port: '3080'
        }
    },
    test: {
        //url to be used in link generation
        //url: 'http://my.site.com',
        //mongodb connection settings
        database: {
            host:   '127.0.0.1',
            //port:   '27017',
            db:     'site_dev',
            user: 'dbuser',
            pass: 'dbpass'
        },
        bw: {
            host: 'virps0esb20i03',
            port: '3080'
        }
    },
    production: {
        //url to be used in link generation
        //url: 'http://my.site.com',
        //mongodb connection settings
        database: {
            host:   '127.0.0.1',
            //port:   '27017',
            db:     'site_dev',
            user: 'dbuser',
            pass: 'dbpass'
        },
        bw: {
            host: 'virps0esb20i03',
            port: '3080'
        }
    }
};
module.exports = config;