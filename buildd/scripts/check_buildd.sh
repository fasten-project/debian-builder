#!/bin/bash

/etc/init.d/buildd status
if [ $? != 0 ]; then
        /etc/init.d/buildd restart
fi
