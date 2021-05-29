
import ivy_init
import sys
import json
import platform
import os

def usage():
    print "usage: \n {} {{option=value...}} <file>.dsc".format(sys.argv[0])
    sys.exit(1)

next_unused_port = 49123

def get_unused_port(protocol):
    global next_unused_port
    next_unused_port += 1
    return next_unused_port

def lookup_ip_addr(hostname):
    return '0x7f000001'

def run_in_terminal(cmd):
    # if platform.system() == 'Darwin':
    #     from applescript import tell
    #     term_cmd = cmd.replace('"','\\"')
    #     tell.app( 'Terminal', 'do script "' + term_cmd + '"')
    os.system("xterm -e '{}'\n".format(cmd))
    
def main():
    ivy_init.read_params()
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        usage()
    dscfname = sys.argv[1]
    try:
        with open(dscfname) as inp:
            try:
                descriptor = json.load(inp)
            except json.JSONDecodeError as err:
                sys.stderr.write("error in {}: {}".format(dscfname,err.msg))
                sys.exit(1)
    except:
        sys.stderr.write('not found: {}\n'.format(dscfname))
        sys.exit(1)

    hosts = {}
    processes = descriptor['processes']
    for process in processes:
        hosts[process['name']] = 'localhost'

    param_vals = {}

    for process in processes:
        for param in process['params']:
            if param['type'] == 'udp.endpoint':
                if param['name'].startswith(process['name']+'.') or process['name'] == 'extract' or process['name'] == 'this':
                    port = get_unused_port('udp')
                    id = '"{{addr:{},port:{}}}"'.format(lookup_ip_addr(hosts[process['name']]),port)
                    if param['name'] in param_vals:
                        sys.stderr.write("endpoint {} is used by multiple processes".format(param['name']))
                        sys.exit(1)
                    param_vals[param['name']] = id

    for process in processes:
        binary = process['binary']
        cmd = [binary if '/' in binary else './' + binary]
        for param in process['params']:
            if param['name'] in param_vals:
                val = param_vals[param['name']]
                if hasattr(param,'default'):
                    cmd.append('{}={}'.format(param['name'],val))
                else:
                    cmd.append('{}'.format(val))
        print ' '.join(cmd)
        run_in_terminal(' '.join(cmd))
        
        
if __name__ == "__main__":
    main()
