import argparse
import sys
import os
import shutil
import glob
import time
import re

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--app_ident", dest="app_ident", help="the id in the endpoint record unique to this interface listener")
parser.add_argument("-i", "--input", dest="tmpl_location", help="the directory of the outbound template application")
parser.add_argument("-o", "--output", dest="app_out_location", help="the directory to output the renamed package")
parser.add_argument("-p", "--port", dest="port", help="if you want to set the LLP Port on generation")
parser.add_argument("-d", "--host", dest="host", help="if you want to set the LLP Host on generation")
parser.add_argument("-m", "--msinterval", dest="msinterval", help="if you want to set the msInterval on generation")
parser.add_argument("-n", "--numretry", dest="numretry", help="if you want to set the numRetry on generation")
args = parser.parse_args(sys.argv[1:])


def generateOutboundBWApp(args):
    print('Generating Outbound Endpoint Application')
    outbound = "c:/OASIS/bw_workspace/translation_engine/template.outbound"
    outbound_app = "c:/OASIS/bw_workspace/translation_engine/template.outbound.application"
    output_dir = "c:/OASIS/bw_workspace/endpoint_apps/"
    receiver_out = args.app_ident+'.outbound'
    receiver_app_out = args.app_ident+'.outbound.application'
    if args.tmpl_location is not None:
        outbound = os.path.join(args.tmpl_location, "template.outbound")
        outbound_app = os.path.join(args.tmpl_location, "template.outbound.application")
    if args.app_out_location is not None:
        output_dir = args.app_out_location
    #lets copy the folder with new name
    n_rec_path = os.path.join(output_dir, receiver_out)
    n_rec_app_path = os.path.join(output_dir, receiver_app_out)
    # todo add ability to overwrite
    if os.path.exists(n_rec_path):
        shutil.rmtree(n_rec_path)
    if os.path.exists(n_rec_app_path):
        shutil.rmtree(n_rec_app_path)
    print('Copying '+outbound+' to '+n_rec_path)
    shutil.copytree(outbound, n_rec_path)
    print('Copying '+outbound_app+' to '+n_rec_app_path)
    shutil.copytree(outbound_app, n_rec_app_path)
    #lets pause after copy before mods just cause I was seeing some missed mods and copying on windows
    time.sleep(5)
    # rename iml file
    #shutil.move(os.path.join(n_rec_path,'template.outbound.iml'), os.path.join(n_rec_path, args.app_ident+'.outbound.iml'))

    # edit build.properties
    with open(os.path.join(n_rec_path,'newbuild.properties'), 'w') as nb:
        with open(os.path.join(n_rec_path,'build.properties')) as b:
            for line in b.readlines():
                # print(line)
                nb.write(line.replace('template.outbound.iml', args.app_ident+'.outbound.iml'))
    os.remove(os.path.join(n_rec_path, 'build.properties'))
    shutil.move(os.path.join(n_rec_path, 'newbuild.properties'), os.path.join(n_rec_path,'build.properties'))
    # change .project name
    with open(os.path.join(n_rec_path, '.newproject'), 'w') as nb:
        with open(os.path.join(n_rec_path, '.project')) as b:
            for line in b.readlines():
                # print(line)
                nb.write(line.replace('<name>template.outbound</name>', '<name>'+args.app_ident+'.outbound</name>'))
    os.remove(os.path.join(n_rec_path, '.project'))
    shutil.move(os.path.join(n_rec_path, '.newproject'), os.path.join(n_rec_path, '.project'))
    
    # edit manifest
    with open(os.path.join(n_rec_path, 'META-INF', 'NEWMANIFEST.MF'), 'w') as nb:
        with open(os.path.join(n_rec_path, 'META-INF', 'MANIFEST.MF')) as b:
            for line in b.readlines():
                #print(line)
                #print(line.replace('template.outbound', args.app_ident+'.outbound'))
                nb.write(line.replace('template.outbound', args.app_ident+'.outbound'))
    os.remove(os.path.join(n_rec_path, 'META-INF', 'MANIFEST.MF'))
    shutil.move(os.path.join(n_rec_path, 'META-INF', 'NEWMANIFEST.MF'), os.path.join(n_rec_path, 'META-INF', 'MANIFEST.MF'))
    
    # need to change META-INF/module.bwm, and the processes sub dirs folder, Activator.bwp, and Outbound.bwp to update the getendpointconfig proc name with package
    with open(os.path.join(n_rec_path, 'META-INF', 'newmodule.bwm'), 'w') as nb:
        with open(os.path.join(n_rec_path, 'META-INF', 'module.bwm')) as b:
            for line in b.readlines():
                #print(line)
                #print(line.replace('template.outbound', args.app_ident+'.outbound'))
                line = line.replace('processName="org.carenet.oasis.hl7.outbound.Outbound"', 'processName="org.carenet.oasis.hl7.'+args.app_ident+'.outbound.Outbound"')
                line = line.replace('processName="template.outbound.Activator"', 'processName="template.'+args.app_ident+'.outbound.Activator"')
                nb.write(line)
    os.remove(os.path.join(n_rec_path, 'META-INF', 'module.bwm'))
    shutil.move(os.path.join(n_rec_path, 'META-INF', 'newmodule.bwm'), os.path.join(n_rec_path, 'META-INF', 'module.bwm'))

    # rename process sub dirs
    shutil.move(os.path.join(n_rec_path, 'Processes', 'org', 'carenet', 'oasis', 'hl7', 'outbound'),
                os.path.join(n_rec_path, 'Processes', 'org', 'carenet', 'oasis', 'hl7', args.app_ident+'.outbound'))
    shutil.move(os.path.join(n_rec_path, 'Processes', 'template', 'outbound'),
                os.path.join(n_rec_path, 'Processes', 'template', args.app_ident+'.outbound'))
    # rename reference in Activator.bwp
    with open(os.path.join(n_rec_path, 'Processes', 'template', args.app_ident+'.outbound', 'newActivator.bwp'), 'w') as nb:
        with open(os.path.join(n_rec_path, 'Processes', 'template', args.app_ident+'.outbound', 'Activator.bwp')) as b:
            for line in b.readlines():
                #print(line)
                #print(line.replace('template.outbound', args.app_ident+'.outbound'))
                line = line.replace('name="template.outbound.Activator"', 'name="template.'+args.app_ident+'.outbound.Activator"')
                line = line.replace('subProcessName="org.carenet.oasis.hl7.outbound.getEndpointConfig"',
                                      'subProcessName="org.carenet.oasis.hl7.'+args.app_ident+'.outbound.getEndpointConfig"')
                nb.write(line)
    os.remove(os.path.join(n_rec_path, 'Processes', 'template', args.app_ident+'.outbound', 'Activator.bwp'))
    shutil.move(os.path.join(n_rec_path, 'Processes', 'template', args.app_ident+'.outbound', 'newActivator.bwp'),
                os.path.join(n_rec_path, 'Processes', 'template', args.app_ident+'.outbound', 'Activator.bwp'))
    # rename reference in Outbound.bwp
    with open(os.path.join(n_rec_path, 'Processes', 'org', 'carenet', 'oasis', 'hl7', args.app_ident+'.outbound', 'newOutbound.bwp'), 'w') as nb:
        with open(os.path.join(n_rec_path, 'Processes', 'org', 'carenet', 'oasis', 'hl7', args.app_ident+'.outbound', 'Outbound.bwp')) as b:
            for line in b.readlines():
                #print(line)
                #print(line.replace('template.outbound', args.app_ident+'.outbound'))
                line = line.replace('name="org.carenet.oasis.hl7.outbound.Outbound"', 'name="org.carenet.oasis.hl7.'+args.app_ident+'.outbound.Outbound"')
                line = line.replace('subProcessName="org.carenet.oasis.hl7.outbound.getEndpointConfig"',
                                      'subProcessName="org.carenet.oasis.hl7.'+args.app_ident+'.outbound.getEndpointConfig"')
                nb.write(line)
    os.remove(os.path.join(n_rec_path, 'Processes', 'org', 'carenet', 'oasis', 'hl7', args.app_ident+'.outbound', 'Outbound.bwp'))
    shutil.move(os.path.join(n_rec_path, 'Processes', 'org', 'carenet', 'oasis', 'hl7', args.app_ident+'.outbound', 'newOutbound.bwp'),
                os.path.join(n_rec_path, 'Processes', 'org', 'carenet', 'oasis', 'hl7', args.app_ident+'.outbound', 'Outbound.bwp'))
    # rename name in getEndpointConfig.bwp
    with open(os.path.join(n_rec_path, 'Processes', 'org', 'carenet', 'oasis', 'hl7', args.app_ident+'.outbound', 'newgetEndpointConfig.bwp'), 'w') as nb:
        with open(os.path.join(n_rec_path, 'Processes', 'org', 'carenet', 'oasis', 'hl7', args.app_ident+'.outbound', 'getEndpointConfig.bwp')) as b:
            for line in b.readlines():
                #print(line)
                #print(line.replace('template.outbound', args.app_ident+'.outbound'))
                line = line.replace('name="org.carenet.oasis.hl7.outbound.getEndpointConfig"', 'name="org.carenet.oasis.hl7.'+args.app_ident+'.outbound.getEndpointConfig"')
                #line = line.replace('subProcessName="org.carenet.oasis.hl7.outbound.getEndpointConfig"',
                #                    'subProcessName="org.carenet.oasis.hl7.'+args.app_ident+'.outbound.getEndpointConfig"')
                nb.write(line)
    os.remove(os.path.join(n_rec_path, 'Processes', 'org', 'carenet', 'oasis', 'hl7', args.app_ident+'.outbound', 'getEndpointConfig.bwp'))
    shutil.move(os.path.join(n_rec_path, 'Processes', 'org', 'carenet', 'oasis', 'hl7', args.app_ident+'.outbound', 'newgetEndpointConfig.bwp'),
                os.path.join(n_rec_path, 'Processes', 'org', 'carenet', 'oasis', 'hl7', args.app_ident+'.outbound', 'getEndpointConfig.bwp'))
    
    #rename processes/template folder
    #shutil.move(os.path.join(n_rec_path, 'Processes', 'template'), os.path.join(n_rec_path, 'Processes', args.app_ident))
    
    #rename template app .project name
    with open(os.path.join(n_rec_app_path, '.newproject'), 'w') as nb:
        with open(os.path.join(n_rec_app_path, '.project')) as b:
            for line in b.readlines():
                # print(line)
                nb.write(line.replace('<name>template.outbound.application</name>', '<name>'+args.app_ident+'.outbound.application</name>'))
    os.remove(os.path.join(n_rec_app_path, '.project'))
    shutil.move(os.path.join(n_rec_app_path, '.newproject'), os.path.join(n_rec_app_path, '.project'))
    
    #rename template app .config id
    with open(os.path.join(n_rec_app_path, '.newconfig'), 'w') as nb:
        with open(os.path.join(n_rec_app_path, '.config')) as b:
            for line in b.readlines():
                # print(line)
                nb.write(line.replace('<projectDetails id="template.outbound.application">', '<projectDetails id="'+args.app_ident+'.outbound.application">'))
    os.remove(os.path.join(n_rec_app_path, '.config'))
    shutil.move(os.path.join(n_rec_app_path, '.newconfig'), os.path.join(n_rec_app_path, '.config'))

    print('Editing: '+os.path.join(n_rec_path, '.config'))
    print('Replacing: <projectDetails id="com.example.templateoutbound with: <projectDetails id="com.example.'+re.sub('[^A-Za-z0-9]+', '', args.app_ident.lower())+'outbound">')
    #rename template app .config id
    with open(os.path.join(n_rec_path, '.newconfig'), 'w') as nb:
        with open(os.path.join(n_rec_path, '.config')) as b:
            for line in b.readlines():
                # BW seems to not like the id having upper case or dashes or periods and at some point changes the template to templateoutbound
                # instead of template.outbound so lets search and adjust for what BW wants to start with
                # print(line)
                nb.write(line.replace('<projectDetails id="com.example.templateoutbound">', '<projectDetails id="com.example.'+re.sub('[^A-Za-z0-9]+', '', args.app_ident.lower())+'outbound">'))
    os.remove(os.path.join(n_rec_path, '.config'))
    shutil.move(os.path.join(n_rec_path, '.newconfig'), os.path.join(n_rec_path, '.config'))

    # rename module include
    
    with open(os.path.join(n_rec_app_path, 'META-INF', 'NEWTIBCO.xml'), 'w') as nb:
        with open(os.path.join(n_rec_app_path, 'META-INF', 'TIBCO.xml')) as b:
            for line in b.readlines():
                # print(line)
                nb.write(line.replace('template.outbound', args.app_ident+'.outbound'))
    os.remove(os.path.join(n_rec_app_path, 'META-INF', 'TIBCO.xml'))
    shutil.move(os.path.join(n_rec_app_path, 'META-INF', 'NEWTIBCO.xml'), os.path.join(n_rec_app_path, 'META-INF', 'TIBCO.xml'))

    # edit app package manifest
    with open(os.path.join(n_rec_app_path, 'META-INF', 'NEWMANIFEST.MF'), 'w') as nb:
        with open(os.path.join(n_rec_app_path, 'META-INF', 'MANIFEST.MF')) as b:
            for line in b.readlines():
                #print(line)
                #print(line.replace('template.outbound', args.app_ident+'.outbound'))
                nb.write(line.replace('template.outbound', args.app_ident+'.outbound'))
    os.remove(os.path.join(n_rec_app_path, 'META-INF', 'MANIFEST.MF'))
    shutil.move(os.path.join(n_rec_app_path, 'META-INF', 'NEWMANIFEST.MF'), os.path.join(n_rec_app_path, 'META-INF', 'MANIFEST.MF'))

    #get all the profile variable files and loop through changing property names referencing template
    profiles = glob.glob(os.path.join(n_rec_app_path, 'META-INF', '*.substvar'))
    #print(profiles)
    for p in profiles:
        with open(os.path.join(n_rec_app_path, 'META-INF', 'tmp.substvar'), 'w', newline='\n') as t:
            with open(p, 'r', newline='\n') as pi:
                # this is funky but parsing xml with prop name line above int val to replace means code to parse xml
                # or do this ugly thing
                nextLineIs_msInterval = False
                nextLineIs_numRetry = False
                for line in pi:
                    # print(len(line.rstrip()))
                    # print(line)
                    # look for template.outbound and template.bw_process_ident
                    line = line.replace('template.outbound', args.app_ident+'.outbound')
                    line = line.replace('<value>template.bw_process_ident</value>', '<value>'+args.app_ident+'</value>')
                    #look for the int props before we set to true for next line
                    if nextLineIs_msInterval:
                        print('Replacing with '+args.msinterval)
                        line = '\t\t\t<value>'+args.msinterval+'</value>\n'
                        nextLineIs_msInterval = False
                    if nextLineIs_numRetry:
                        print('Replacing with '+args.numretry)
                        line = '\t\t\t<value>'+args.numretry+'</value>\n'
                        nextLineIs_numRetry = False
                    if args.port is not None:
                        line = line.replace('template.port', args.port)
                    if args.host is not None:
                        line = line.replace('template.host', args.host)
                    if 'msInterval' in line:
                        print('Found msInterval to replace')
                        nextLineIs_msInterval = True
                    if 'numRetry' in line:
                        print('Found numretry to replace')
                        nextLineIs_numRetry = True
                    t.write(line)
        os.remove(p)
        shutil.move(os.path.join(n_rec_app_path, 'META-INF','tmp.substvar'),p)
    profiles = glob.glob(os.path.join(n_rec_path, 'META-INF', '*.substvar'))
    print('Editing the profile files properties')
    #print(profiles)
    for p in profiles:
        with open(os.path.join(n_rec_path, 'META-INF','tmp.substvar'), 'w', newline='\n') as t:
            with open(p, 'r', newline='\n') as pi:
                nextLineIs_msInterval = False
                nextLineIs_numRetry = False
                for line in pi.readlines():
                    line = line.replace('template.receiver', args.app_ident+'.receiver')
                    line = line.replace('template.outbound', args.app_ident+'.outbound')
                    line = line.replace('<value>template.bw_process_ident</value>', '<value>'+args.app_ident+'</value>')
                    if nextLineIs_msInterval:
                        print('Replacing with '+args.msinterval)
                        line = '\t\t\t<value>'+args.msinterval+'</value>\n'
                        nextLineIs_msInterval = False
                    if nextLineIs_numRetry:
                        print('Replacing with '+args.numretry)
                        line = '\t\t\t<value>'+args.numretry+'</value>\n'
                        nextLineIs_numRetry = False
                    if args.port is not None:
                        line = line.replace('template.port', args.port)
                    if args.host is not None:
                        line = line.replace('template.host', args.host)
                    if 'msInterval' in line:
                        print('Found msInterval to replace')
                        nextLineIs_msInterval = True
                    if 'numRetry' in line:
                        print('Found numretry to replace')
                        nextLineIs_numRetry = True
                    t.write(line)
        os.remove(p)
        shutil.move(os.path.join(n_rec_path, 'META-INF','tmp.substvar'), p)
generateOutboundBWApp(args)

