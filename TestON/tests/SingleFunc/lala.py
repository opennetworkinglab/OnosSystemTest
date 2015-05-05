        main.log.report()
        main.log.case()
        main.step()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="",
                                 onfail="" )
