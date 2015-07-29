class FVTADD :
    def __init__(self):
        self.default = ''


    def runTest(self,self) :
        return TemplateTest.runTest(self)

    def tearDown(self,self) :
        return TemplateTest.tearDown(self)

    def setUp(self,self) :
        return TemplateTest.setUp(self)

    def chkSetUpCondition(self,self,fv,sv_ret,ctl_ret,sw_ret) :
        return TemplateTest.chkSetUpCondition(self,fv,sv_ret,ctl_ret,sw_ret)
