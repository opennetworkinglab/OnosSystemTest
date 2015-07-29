class Pronto:
    def __init__( self ):
        self.prompt = '(.*)'
        self.timeout = 60

    def status(self, *options, **def_args ):
        '''Possible Options :['Pronto-CLI']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "status "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def port_show_*(self, *options, **def_args ):
        '''Possible Options :['Pronto-CLI']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "port show * "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def status_ProntoCLI(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "status Pronto-CLI "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def port_show_*_ProntoCLI(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "port show * Pronto-CLI "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

