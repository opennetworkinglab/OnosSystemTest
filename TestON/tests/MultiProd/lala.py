
        # main.step(var1)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            ingressDevice="of:0000000000003008/1",
            egressDevice="of:0000000000006018/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h8' ))
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            ingressDevice="of:0000000000006018/1",
            egressDevice="of:0000000000003008/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h18' ))
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var2 = "Add point intents for mn hosts h9&h19 or ONOS hosts h9&h13"
        main.step(var2)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003009/1",
            "of:0000000000006019/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h9' ))
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006019/1",
            "of:0000000000003009/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h19' ))
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var3 = "Add point intents for MN hosts h10&h20 or ONOS hosts hA&h14"
        main.step(var3)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003010/1",
            "of:0000000000006020/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h10' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006020/1",
            "of:0000000000003010/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h20' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var4 = "Add point intents for mininet hosts h11 and h21 or" +\
               " ONOS hosts hB and h15"
        main.case(var4)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003011/1",
            "of:0000000000006021/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h11' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006021/1",
            "of:0000000000003011/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h21' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var5 = "Add point intents for mininet hosts h12 and h22 " +\
               "ONOS hosts hC and h16"
        main.case(var5)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003012/1",
            "of:0000000000006022/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h12' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006022/1",
            "of:0000000000003012/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h22' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var6 = "Add point intents for mininet hosts h13 and h23 or" +\
               " ONOS hosts hD and h17"
        main.case(var6)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003013/1",
            "of:0000000000006023/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h13' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006023/1",
            "of:0000000000003013/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h23' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var7 = "Add point intents for mininet hosts h14 and h24 or" +\
               " ONOS hosts hE and h18"
        main.case(var7)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003014/1",
            "of:0000000000006024/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h14' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006024/1",
            "of:0000000000003014/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h24' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var8 = "Add point intents for mininet hosts h15 and h25 or" +\
               " ONOS hosts hF and h19"
        main.case(var8)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003015/1",
            "of:0000000000006025/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h15' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006025/1",
            "of:0000000000003015/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h25' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var9 = "Add intents for mininet hosts h16 and h26 or" +\
               " ONOS hosts h10 and h1A"
        main.case(var9)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003016/1",
            "of:0000000000006026/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h16' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006026/1",
            "of:0000000000003016/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h26' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var10 = "Add point intents for mininet hosts h17 and h27 or" +\
                " ONOS hosts h11 and h1B"
        main.case(var10)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003017/1",
            "of:0000000000006027/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h17' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            #main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006027/1",
            "of:0000000000003017/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h27' ))
