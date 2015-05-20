
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003008/1",
            "of:0000000000006018/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h8' ))
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006018/1",
            "of:0000000000003008/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h18' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        main.step(
            "Add point-to-point intents for mininet hosts" +
            " h9 and h19 or ONOS hosts h9 and h13" )
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003009/1",
            "of:0000000000006019/1", )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006019/1",
            "of:0000000000003009/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        main.step(
            "Add point-to-point intents for mininet" +
            " hosts h10 and h20 or ONOS hosts hA and h14" )
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003010/1",
            "of:0000000000006020/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006020/1",
            "of:0000000000003010/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        main.step(
            "Add point-to-point intents for mininet" +
            " hosts h11 and h21 or ONOS hosts hB and h15" )
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003011/1",
            "of:0000000000006021/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006021/1",
            "of:0000000000003011/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        main.step(
            "Add point-to-point intents for mininet" +
            " hosts h12 and h22 or ONOS hosts hC and h16" )
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003012/1",
            "of:0000000000006022/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006022/1",
            "of:0000000000003012/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        main.step(
            "Add point-to-point intents for mininet " +
            "hosts h13 and h23 or ONOS hosts hD and h17" )
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003013/1",
            "of:0000000000006023/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006023/1",
            "of:0000000000003013/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        main.step(
            "Add point-to-point intents for mininet hosts" +
            " h14 and h24 or ONOS hosts hE and h18" )
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003014/1",
            "of:0000000000006024/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006024/1",
            "of:0000000000003014/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        main.step(
            "Add point-to-point intents for mininet hosts" +
            " h15 and h25 or ONOS hosts hF and h19" )
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003015/1",
            "of:0000000000006025/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006025/1",
            "of:0000000000003015/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        main.step(
            "Add point-to-point intents for mininet hosts" +
            " h16 and h26 or ONOS hosts h10 and h1A" )
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003016/1",
            "of:0000000000006026/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006026/1",
            "of:0000000000003016/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        main.step(
            "Add point-to-point intents for mininet hosts h17" +
            " and h27 or ONOS hosts h11 and h1B" )
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003017/1",
            "of:0000000000006027/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006027/1",
            "of:0000000000003017/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )
