#!/usr/local/bin/python
#CHIPSEC: Platform Security Assessment Framework
#Copyright (c) 2010-2014, Intel Corporation
# 
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; Version 2.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#Contact information:
#chipsec@intel.com
#




#
# usage as a standalone utility:
#
## \addtogroup standalone
#
#chipsec_util spi
#-----
#~~~
#chipsec_util spi info|dump|read|write|eraseByGio [flash_address] [length] [file]
#''
#    Examples:
#''
#        chipsec_util spi info
#        chipsec_util spi dump rom.bin
#        chipsec_util spi read 0x700000 0x100000 bios.bin
#        chipsec_util spi write 0x0 flash_descriptor.bin\n
#~~~

__version__ = '1.0'


import os
import sys
import time

import chipsec_util
from chipsec_util import chipsec_util_commands, _cs

from chipsec.logger     import *
from chipsec.file       import *

from chipsec.hal.spi    import *

#_cs = cs()

usage = "chipsec_util uniflash info|dump|read|write|getfirmware [flash_address] [length] [file]\n" + \
        "Examples:\n" + \
        "  chipsec_util uniflash info\n" + \
        "  chipsec_util uniflash getfirmware rom.bin\n" 

chipsec_util.global_usage += usage

# ###################################################################
#
# SPI Flash Controller
#
# ###################################################################

def uniflash(argv):

    if 3 > len(argv):
      print usage
      return

    try:
       spi = SPI( _cs )
    except SpiRuntimeError, msg:
       print msg
       return

    spi_op = argv[2]

    t = time.time()

    if ( 'getfirmware' == spi_op ):
       out_file = 'rom.bin'
       logger().log( "[CHIPSEC] Dumping entire SPI Flash to '%s'" % out_file )
       # @TODO: don't assume SPI Flash always ends with BIOS region
       (base,limit,freg) = spi.get_SPI_region( BIOS )
       spi_size = limit + 1
       logger().log( "[CHIPSEC] BIOS Region: Base = 0x%08X, Limit = 0x%08X" % (base,limit) )
       logger().log( "[CHIPSEC] Dumping 0x%08X bytes (to the end of BIOS region)" % spi_size )
       buf = spi.read_spi_to_file( 0, spi_size, out_file )
       if (buf is None):
          logger().error( "Dumping SPI Flash didn't return any data (turn on VERBOSE)" )
       else:
          logger().log_result( "Done dumping SPI Flash" ) 
    elif ( 'write' == spi_op and 5 == len(argv) ):
       spi_fla = int(argv[3],16)
       filename = argv[4]
       logger().log( "[CHIPSEC] Writing to SPI Flash at FLA = 0x%X from '%.64s'" % (spi_fla, filename) )
       #
       # This write protection only matters for BIOS range in SPI
       # Continue if FLA being written is not within BIOS range 
       # @TODO: do smth smarter here
       #
       if not spi.disable_BIOS_write_protection():
          logger().error( "Could not disable SPI Flash protection. Still trying.." )

       ok = spi.write_spi_from_file( spi_fla, filename )
       if ok: logger().log_result( "SPI Flash write done" )
       else:  logger().warn( "SPI Flash write returned error (turn on VERBOSE)" )
    elif ( 'read' == spi_op ):
       spi_fla = int(argv[3],16)
       length = int(argv[4],16)
       logger().log( "[CHIPSEC] Reading 0x%x bytes from SPI Flash starting at FLA = 0x%X" % (length, spi_fla) )
       out_file = None
       if 6 == len(argv):
          out_file = argv[5]
       buf = spi.read_spi_to_file( spi_fla, length, out_file )
       if (buf is None):
          logger().error( "SPI Flash read didn't return any data (turn on VERBOSE)" )
       else:
          logger().log_result( "SPI Flash read done" )
    elif ( 'info' == spi_op ):
       logger().log( "[CHIPSEC] SPI Flash Info\n" )
       ok = spi.display_SPI_map()
    elif ( 'dump' == spi_op ):
       out_file = 'rom.bin'
       if 4 == len(argv):
          out_file = argv[3]
       logger().log( "[CHIPSEC] Dumping entire SPI Flash to '%s'" % out_file )
       # @TODO: don't assume SPI Flash always ends with BIOS region
       (base,limit,freg) = spi.get_SPI_region( BIOS )
       spi_size = limit + 1
       logger().log( "[CHIPSEC] BIOS Region: Base = 0x%08X, Limit = 0x%08X" % (base,limit) )
       logger().log( "[CHIPSEC] Dumping 0x%08X bytes (to the end of BIOS region)" % spi_size )
       buf = spi.read_spi_to_file( 0, spi_size, out_file )
       if (buf is None):
          logger().error( "Dumping SPI Flash didn't return any data (turn on VERBOSE)" )
       else:
          logger().log_result( "Done dumping SPI Flash" ) 
    else:
       print usage
       return

    logger().log( "[CHIPSEC] (spi %s) time elapsed %.3f" % (spi_op, time.time()-t) )



chipsec_util_commands['uniflash'] = {'func' : uniflash,     'start_driver' : True  }

