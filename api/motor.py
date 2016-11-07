#! encoding = utf-8

def move(motorHandle, step):
    '''
        Move motor by step
    '''

    motorHandle.write('1PA+{:d}\n'.format(step))
