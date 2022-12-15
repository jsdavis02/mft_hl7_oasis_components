var config = {
    local: {
        //url to be used in link generation
        //url: 'http://my.site.com',
        //mongodb connection settings
        env: 'DEV',
        database: {
            host:   'VIRPS0INF20D61',
            //port:   '27017',
            db:     'oasis',
            user: 'srvPS0TBC20OAS',
            pass: 'SRu&Ti%x$se9&t#ynWVy'
        },
        bw: {
            host: 'virps0esb20i03',
            port: '3080',
            mft_port: '8100',
            ops_port: '5556',
            queuelist: 'C:\\OASIS\\queuelist.txt'
        },
        encryption: {
            secret: Buffer.from('5C9830C36AA063E7230895089D486BDV', 'utf8')
        },
        email: {
            smtp: {
                host: 'relay.hs.maricopa.gov',
                port: 25,
                secure: false,
                tls: {
                    // do not fail on invalid certs
                    rejectUnauthorized: false
                },    
            },
        }
    },
    development: {
        //url to be used in link generation
        //url: 'http://my.site.com',
        //mongodb connection settings
        env: 'DEV',
        database: {
            host:   'VIRPS0INF20D61',
            //port:   '27017',
            db:     'oasis',
            user: 'srvPS0TBC20OAS',
            pass: 'SRu&Ti%x$se9&t#ynWVy'
        },
        bw: {
            host: 'virps0esb20i03',
            port: '3080',
            mft_port: '8100',
            ops_port: '5556',
            queuelist: '/opt/oasis_data/monitoring/queuelist.txt'
        },
        encryption: {
            secret: Buffer.from('5C9830C36AA063E7230895089D486BDV', 'utf8')
        },
        email: {
            smtp: {
                host: 'relay.hs.maricopa.gov',
                port: 25,
                secure: false,
                tls: {
                    // do not fail on invalid certs
                    rejectUnauthorized: false
                },
            },
        }
    },
    test: {
        //url to be used in link generation
        //url: 'http://my.site.com',
        //mongodb connection settings
        env: 'TST',
        database: {
            host:   'VIRPS0INF30D61',
            //port:   '27017',
            db:     'oasis',
            user: 'srvPS0TBC30OAS',
            pass: 'k2!ZI@#rUA+cKCT7_*d'
        },
        bw: {
            host: 'virps0esb30i03',
            port: '3080',
            mft_port: '8100',
            ops_port: '5556',
            queuelist: '/opt/oasis_data/monitoring/queuelist.txt'
        },
        encryption: {
            secret: Buffer.from('5C9830C36AA063E7230895089D486BDV', 'utf8')
        },
        email: {
            smtp: {
                host: 'relay.hs.maricopa.gov',
                port: 25,
                secure: false,
                tls: {
                    // do not fail on invalid certs
                    rejectUnauthorized: false
                },
            },
        }
    },
    preproduction: {
        //url to be used in link generation
        //url: 'http://my.site.com',
        //mongodb connection settings
        env: 'PPRD',
        database: {
            host:   'L01PS0INF40DA01',
            //port:   '27017',
            db:     'oasis',
            user: 'srvPS0TBC40OAS',
            pass: 'vPptzX3y_K4#n6Lr!Ex'
        },
        bw: {
            host: 'virps0esb40i04',
            port: '3080',
            mft_port: '8100',
            ops_port: '5556',
            queuelist: '/opt/oasis_data/monitoring/queuelist.txt'
        },
        encryption: {
            secret: Buffer.from('5C9830C36AA063E7230895089D486BDV', 'utf8')
        },
        email: {
            smtp: {
                host: 'relay.hs.maricopa.gov',
                port: 25,
                secure: false,
                tls: {
                    // do not fail on invalid certs
                    rejectUnauthorized: false
                },
            },
        }
    },
    production: {
        //url to be used in link generation
        //url: 'http://my.site.com',
        //mongodb connection settings
        env: 'PRD',
        database: {
            host:   'L01PS0INF50DA01',
            //port:   '27017',
            db:     'oasis',
            user: 'srvPS0TBC50OAS',
            pass: 'Fn5#u4ubCIWDl1_3a3!'
        },
        bw: {
            host: 'virps0esb50i05',
            port: '3080',
            mft_port: '8100',
            ops_port: '5556',
            queuelist: '/opt/oasis_data/monitoring/queuelist.txt'
        },
        encryption: {
            secret: Buffer.from('5C9830C36AA063E7230895089D486BDV', 'utf8')
        },
        email: {
            smtp: {
                host: 'relay.hs.maricopa.gov',
                port: 25,
                secure: false,
                tls: {
                    // do not fail on invalid certs
                    rejectUnauthorized: false
                },
            },
        }
    }
};
module.exports = config;