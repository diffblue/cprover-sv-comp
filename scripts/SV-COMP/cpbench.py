import os
import shutil


def get_source_root_dir():
    return os.path.abspath(os.path.join("..", "..", "sv-benchmarks-fork-marek-trtik", "c"))


def get_destination_root_dir():
    return os.path.abspath(os.path.join("..", "..", "sv-benchmarks", "c"))


"""



"""


def _main():
    for bench_rpath in [
            # "float-benchs/inv_Newton_false-unreach-call.c"
            #
            # "ntdrivers/floppy2_true-unreach-call_true-termination.i.cil.c",
            # "ntdrivers/floppy_true-unreach-call_true-valid-memsafety.i.cil.c",
            # "ntdrivers/parport_true-unreach-call.i.cil.c",
            #
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-43_2a-drivers--media--usb--s2255--s2255drv.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-32_7a-drivers--media--usb--dvb-usb--dvb-usb-opera.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-43_2a-drivers--usb--serial--digi_acceleport.ko-entry_point_true-unreach-call.cil.out.c",
            #
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-32_7a-drivers--misc--sgi-gru--gru.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-32_7a-drivers--net--wireless--prism54--prism54.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-43_2a-drivers--net--appletalk--ipddp.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-43_2a-drivers--net--wireless--prism54--prism54.ko-entry_point_true-unreach-call.cil.out.c",
            #
            # "ldv-linux-3.4-simple/43_1a_cilled_true-unreach-call_ok_nondet_linux-43_1a-drivers--acpi--container.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/43_1a_cilled_true-unreach-call_ok_nondet_linux-43_1a-drivers--acpi--fan.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/43_1a_cilled_true-unreach-call_ok_nondet_linux-43_1a-drivers--platform--x86--panasonic-laptop.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/43_1a_cilled_true-unreach-call_ok_nondet_linux-43_1a-drivers--platform--x86--topstar-laptop.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/43_1a_cilled_true-unreach-call_ok_nondet_linux-43_1a-drivers--power--test_power.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            #
            # "ldv-commit-tester/main0_true-unreach-call_drivers-media-video-tlg2300-poseidon-ko--32_7a--4a349aa.c",
            # "ldv-commit-tester/main3_true-unreach-call_drivers-media-video-tlg2300-poseidon-ko--32_7a--4a349aa-1_false-termination.c",
            # "ldv-commit-tester/main3_true-unreach-call_drivers-media-video-tlg2300-poseidon-ko--32_7a--4a349aa_false-termination.c",
            #
            # "ldv-consumption/32_7a_cilled_true-unreach-call_linux-3.8-rc1-32_7a-drivers--block--paride--pf.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-consumption/32_7a_cilled_true-unreach-call_linux-3.8-rc1-32_7a-net--batman-adv--batman-adv.ko-ldv_main15_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-consumption/32_7a_cilled_true-unreach-call_linux-3.8-rc1-drivers--block--paride--pcd.ko-main.cil.out.c",
            # "ldv-consumption/32_7a_cilled_true-unreach-call_linux-3.8-rc1-drivers--block--paride--pf.ko-main.cil.out.c",
            #
            # "list-ext-properties/list-ext_flag_false-unreach-call_false-valid-deref.i",
            # "ldv-memsafety/memset2_false-valid-deref-write.c",
            # "ldv-memsafety/memset3_false-valid-deref-write.c",
            # "ldv-memsafety/memsetNonZero2_false-valid-deref-write.c",
            # "ldv-memsafety/memsetNonZero3_false-valid-deref-write.c",
            # "ldv-memsafety/memsetNonZero_false-valid-deref-write.c",
            # "ldv-memsafety/memset_false-valid-deref-write.c",
            # "ldv-memsafety-bitfields/test-bitfields-2.1_true-valid-memsafety.i",
            # "ldv-memsafety-bitfields/test-bitfields-2_false-valid-deref.i",
            # "ldv-memsafety-bitfields/test-bitfields-3.1_false-valid-deref.i",
            # "ldv-memsafety-bitfields/test-bitfields-3_false-valid-deref.i",
            #
            # "ldv-memsafety-bitfields/test-bitfields-1_true-valid-memsafety_true-termination.i",
            # "busybox-1.22.0/chgrp-incomplete_true-no-overflow_false-valid-memtrack.i",
            # "busybox-1.22.0/chroot-incomplete_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/echo_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/fold_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/logname_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/mkfifo-incomplete_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/readlink_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/realpath_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/sync_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/tac_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/tee_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/uname_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/uniq_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/usleep_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/who_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/whoami-incomplete_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/yes_true-no-overflow_true-valid-memsafety.i",
            #
            # "ldv-races/race-4_1-thread_local_vars_true-unreach-call.i",
            #
            # "heap-manipulation/bubble_sort_linux_false-unreach-call_false-valid-memcleanup.i",
            # "heap-manipulation/bubble_sort_linux_true-unreach-call_true-valid-memsafety.i",
            # "ntdrivers/cdaudio_false-unreach-call.i.cil.c",
            # "ntdrivers/cdaudio_true-unreach-call.i.cil.c",
            # "ldv-sets/test_add_false-unreach-call_true-termination.i",
            # "ldv-sets/test_mutex_double_lock_false-unreach-call_true-termination.i",
            # "ldv-sets/test_mutex_double_unlock_false-unreach-call.i",
            # "ldv-sets/test_mutex_unbounded_false-unreach-call.i",
            # "memsafety/test-0137_false-valid-deref.i",
            # "ldv-sets/test_add_false-unreach-call_true-termination.i",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-43_2a-drivers--scsi--device_handler--scsi_dh_rdac.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-32_7a-drivers--net--wireless--libertas--libertas.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-32_7a-drivers--mtd--ubi--ubi.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-08_1a-drivers--scsi--st.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-43_2a-drivers--scsi--megaraid--megaraid_mm.ko-entry_point_false-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-32_7a-drivers--input--mousedev.ko-entry_point_false-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-32_7a-drivers--gpu--drm--mgag200--mgag200.ko-entry_point_false-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-08_1a-drivers--iio--accel--kxcjk-1013.ko-entry_point_false-unreach-call.cil.out.c",
            # "ldv-validator-v0.8/linux-stable-063f96c-1-144_2a-drivers--mmc--host--vub300.ko.unsigned-entry_point_ldv-val-v0.8_false-unreach-call.cil.out.c",
            #
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-43_2a-drivers--usb--serial--io_edgeport.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-43_2a-drivers--bluetooth--hci_uart.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-32_7a-drivers--power--bq2415x_charger.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-08_1a-drivers--scsi--sg.ko-entry_point_false-unreach-call.cil.out.c",
            # "ldv-validator-v0.8/linux-stable-4a349aa-1-32_7a-drivers--media--video--tlg2300--poseidon.ko-entry_point_ldv-val-v0.8_false-unreach-call.cil.out.c",
            # "ldv-validator-v0.8/linux-stable-064368f-1-111_1a-drivers--media--radio--si4713-i2c.ko-entry_point_ldv-val-v0.8_false-unreach-call.cil.out.c",
            #
            # "loop-industry-pattern/ofuf_1_true-unreach-call.c",
            # "loop-industry-pattern/ofuf_1_true-unreach-call.c",
            # "loop-industry-pattern/ofuf_2_true-unreach-call.c",
            # "loop-industry-pattern/ofuf_3_true-unreach-call.c",
            # "loop-industry-pattern/ofuf_4_true-unreach-call.c",
            # "loop-industry-pattern/ofuf_5_true-unreach-call.c",
            #
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-43_2a-drivers--net--ethernet--atheros--alx--alx.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-43_2a-drivers--net--ethernet--intel--ixgb--ixgb.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-43_2a-drivers--net--ethernet--marvell--skge.ko-entry_point_true-unreach-call.cil.out.c",
            #
            # "ldv-linux-3.4-simple/43_1a_cilled_true-unreach-call_ok_nondet_linux-43_1a-drivers--power--test_power.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-32_7a-drivers--media--usb--dvb-usb--dvb-usb-opera.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-43_2a-drivers--media--usb--s2255--s2255drv.ko-entry_point_true-unreach-call.cil.out.c",
            # "ldv-linux-4.2-rc1/linux-4.2-rc1.tar.xz-43_2a-drivers--usb--serial--digi_acceleport.ko-entry_point_true-unreach-call.cil.out.c",
            #
            # "ldv-memsafety-bitfields/test-bitfields-2_true-valid-memsafety_true-termination.i",
            # "ldv-memsafety-bitfields/test-bitfields-3.1_true-valid-memsafety_true-termination.i",
            #
            # "termination-crafted/WhileTrue_true-no-overflow_false-termination_true-valid-memsafety.c",
            # "termination-restricted-15/Ex05_false-termination_true-no-overflow.c",
            #
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3.4-32_1-drivers--usb--storage--ums-freecom.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3.4-32_1-drivers--usb--storage--ums-jumpshot.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3.4-32_1-drivers--media--dvb--dvb-usb--dvb-usb-az6027.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3.4-32_1-drivers--acpi--fan.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3.4-32_1-drivers--scsi--dmx3191d.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            #
            # "ldv-linux-3.0/usb_urb-drivers-hid-usbhid-usbmouse.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.0/usb_urb-drivers-usb-misc-iowarrior.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.0/usb_urb-drivers-net-usb-catc.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.4-simple/32_7_cpp_false-unreach-call_single_drivers-net-phy-dp83640.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cpp_false-unreach-call_single_drivers-staging-media-dt3155v4l-dt3155v4l.cil.out.c",
            #
            # "ldv-linux-3.0/usb_urb-drivers-hid-usbhid-usbmouse.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.0/usb_urb-drivers-input-misc-keyspan_remote.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.0/usb_urb-drivers-media-dvb-ttusb-dec-ttusb_dec.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.0/usb_urb-drivers-net-can-usb-ems_usb.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.0/usb_urb-drivers-net-usb-catc.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.0/usb_urb-drivers-staging-lirc-lirc_imon.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.0/usb_urb-drivers-usb-misc-iowarrior.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--input--mouse--synaptics_usb_false-termination.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--input--mousedev_true-termination.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--media--dvb--dvb-usb--dvb-usb-dib0700.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--media--video--cpia2--cpia2.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--net--phy--dp83640.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--net--wireless--p54--p54usb.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--staging--keucr--keucr.ko-ldv_main1_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--usb--image--microtek.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--video--aty--atyfb.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cpp_false-unreach-call_single_drivers-net-phy-dp83640.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cpp_false-unreach-call_single_drivers-net-wireless-mwl8k.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cpp_false-unreach-call_single_drivers-net-wireless-p54-p54usb.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cpp_false-unreach-call_single_drivers-staging-media-dt3155v4l-dt3155v4l.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cpp_false-unreach-call_single_drivers-usb-image-microtek.cil.out.c",
            #
            # "ldv-linux-3.0/usb_urb-drivers-hid-usbhid-usbmouse.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--input--misc--ad714x-i2c.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--serial--zio.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cpp_false-unreach-call_single_drivers-net-phy-dp83640.cil.out.c",
            #
            # "pthread-wmm/mix000_power.oepc_false-unreach-call.i",     # OK!
            # "pthread-wmm/mix000_power.opt_false-unreach-call.i",     # OK!
            # "pthread-wmm/mix008_power.oepc_false-unreach-call.i",
            # "pthread-wmm/mix031_pso.oepc_false-unreach-call.i",
            # "pthread-wmm/thin000_rmo.opt_false-unreach-call.i",
            # "pthread-wmm/rfi008_tso.opt_false-unreach-call.i",    # OK!
            #
            # "pthread-lit/fkp2013_variant_false-unreach-call.i",       # PROBLEM! Verification result: UNKNOWN, incomplete analysis.
            # "pthread-lit/qw2004_false-unreach-call.i",
            #
            # "ldv-races/race-1_3-join_false-unreach-call.i",       # OK!
            # "ldv-races/race-4_2-thread_local_vars_false-unreach-call.i",
            #
            # "pthread-driver-races/char_generic_nvram_read_nvram_write_nvram_false-unreach-call.i",      # OK!
            # "pthread-driver-races/char_pc8736x_gpio_pc8736x_gpio_change_pc8736x_gpio_current_false-unreach-call.i",
            # "pthread-driver-races/char_pc8736x_gpio_pc8736x_gpio_change_pc8736x_gpio_set_false-unreach-call.i",
            # "pthread-driver-races/char_pc8736x_gpio_pc8736x_gpio_current_pc8736x_gpio_set_false-unreach-call.i",
            #
            # "pthread-C-DAC/pthread-demo-datarace_false-unreach-call.i",           # OK!
            #
            # "pthread/lazy01_false-unreach-call.i",        # OK!
            # "pthread/fib_bench_false-unreach-call.i",
            # "pthread/fib_bench_longer_false-unreach-call.i",
            # "pthread/fib_bench_longest_false-unreach-call.i",
            # "pthread/queue_longer_false-unreach-call.i",
            # "pthread/queue_longest_false-unreach-call.i",
            #
            # "pthread/stack_false-unreach-call.i",     # PROBLEM! Verification result: UNKNOWN, incomplete analysis. Error: Unsupported C feature (BDD-analysis does not support arrays: stack[__CPAchecker_TMP_1]) (BDDVectorCExpressionVisitor.visit, SEVERE)
            # "pthread/stateful01_false-unreach-call.i",
            # "pthread/stack_longer_false-unreach-call.i",
            # "pthread/stack_longest_false-unreach-call.i",
            #
            # "pthread-atomic/qrcu_false-unreach-call.i",           # OK!
            # "pthread-atomic/read_write_lock_false-unreach-call.i",
            #
            # "pthread-ext/28_buggy_simple_loop1_vf_false-unreach-call.i",      # PROBLEM! Verification result: UNKNOWN, incomplete analysis. Error: Unrecognized code (multiple thread assignments to same LHS not supported: t) (ThreadingTransferRelation.getNewThreadId, SEVERE)
            # "pthread-ext/27_Boop_simple_vf_false-unreach-call.i",
            # "pthread-ext/32_pthread5_vs_false-unreach-call.i",
            # "pthread-ext/25_stack_longer_false-unreach-call.i",
            # "pthread-ext/26_stack_cas_longest_false-unreach-call.i",
            #
            # "pthread-wmm/safe036_power.opt_true-unreach-call.i",        # PROBLEM! Verification result: UNKNOWN, incomplete analysis. Error: line 728: Unsupported feature (pthread_create): pthread_create(&t2629, (void *)0, &P0, (void *)0); (line was originally pthread_create(&t2629, ((void *)0), P0, ((void *)0));) (CallstackTransferRelation.getAbstractSuccessorsForEdge, SEVERE)
            # "pthread-driver-races/char_pc8736x_gpio_pc8736x_gpio_change_pc8736x_gpio_configure_true-unreach-call.i",
            # "pthread-wmm/safe000_pso.opt_true-unreach-call.i",
            #
            # "ldv-linux-3.0/usb_urb-drivers-hid-usbhid-usbmouse.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.0/usb_urb-drivers-input-misc-keyspan_remote.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.0/usb_urb-drivers-media-dvb-ttusb-dec-ttusb_dec.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.0/usb_urb-drivers-net-can-usb-ems_usb.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.0/usb_urb-drivers-net-usb-catc.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.0/usb_urb-drivers-staging-lirc-lirc_imon.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.0/usb_urb-drivers-usb-misc-iowarrior.ko_false-unreach-call.cil.out.i.pp.i",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--input--misc--ad714x-i2c.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--input--misc--mma8450.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--input--misc--mpu3050.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--input--touchscreen--eeti_ts.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--input--touchscreen--max11801_ts.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--leds--leds-pca9633.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--media--dvb--dvb-usb--dvb-usb-cinergyT2.ko-ldv_main1_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--media--dvb--dvb-usb--dvb-usb-dtt200u.ko-ldv_main1_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--media--dvb--dvb-usb--dvb-usb-mxl111sf.ko-ldv_main3_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--media--dvb--dvb-usb--dvb-usb-vp7045.ko-ldv_main1_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--net--usb--cdc_subset.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--net--usb--plusb.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--staging--iio--addac--adt7316-spi.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--staging--iio--meter--ade7854-i2c.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--staging--serqt_usb2--serqt_usb2.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--dwc3--dwc3-pci.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--misc--trancevibrator.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--serial--cp210x.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--serial--empeg.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--serial--funsoft.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--serial--hp4x.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--serial--ipw.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--serial--mos7840.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--serial--moto_modem.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--serial--qcaux.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--serial--siemens_mpi.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--serial--ssu100.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--serial--usb_debug.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--serial--vivopay-serial.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3_false-termination.4-32_1-drivers--usb--serial--zio.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--input--mouse--synaptics_usb_false-termination.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--input--mousedev_true-termination.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--media--dvb--dvb-usb--dvb-usb-dib0700.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--media--video--cpia2--cpia2.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--net--phy--dp83640.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--net--wireless--p54--p54usb.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--staging--keucr--keucr.ko-ldv_main1_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--usb--image--microtek.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cilled_false-unreach-call_const_ok_linux-32_1-drivers--video--aty--atyfb.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cpp_false-unreach-call_single_drivers-net-phy-dp83640.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cpp_false-unreach-call_single_drivers-net-wireless-mwl8k.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cpp_false-unreach-call_single_drivers-net-wireless-p54-p54usb.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cpp_false-unreach-call_single_drivers-staging-media-dt3155v4l-dt3155v4l.cil.out.c",
            # "ldv-linux-3.4-simple/32_7_cpp_false-unreach-call_single_drivers-usb-image-microtek.cil.out.c",
            #
            # "pthread/bigshot_p_false-unreach-call.i",
            # "busybox-1.22.0/chgrp-incomplete_true-no-overflow_false-valid-memtrack.i",
            # "array-memsafety/diff-alloca_true-valid-memsafety_true-termination.i",
            # "array-memsafety/mult_array-alloca_true-valid-memsafety_true-termination.i",
            # "array-memsafety/openbsd_cstrlen-alloca_true-valid-memsafety_true-termination.i",
            # "pthread-wmm/mix003_tso.oepc_false-unreach-call.i",
            # "pthread-wmm/mix006_pso.opt_false-unreach-call.i",
            # "pthread-wmm/mix009_tso.opt_false-unreach-call.i",
            #
            # "busybox-1.22.0/chroot-incomplete_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/logname_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/sync_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/uniq_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/wc_false-unreach-call_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/basename_false-unreach-call_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/usleep_true-no-overflow_true-valid-memsafety.i",
            #
            # "array-memsafety/openbsd_cmemchr-alloca_true-valid-memsafety_true-termination.i",
            # "array-memsafety/openbsd_cstrlen-alloca_true-valid-memsafety_true-termination.i",
            # "array-memsafety/openbsd_cstrstr-alloca_true-valid-memsafety_true-termination.i",
            #
            # "memsafety/test-0504_true-valid-memsafety.i",
            # "memsafety-ext/dll_extends_pointer_true-valid-memsafety.i",
            # "memsafety-ext2/length_test03_false-valid-memtrack.i",
            # "list-ext-properties/test-0513_1_true-valid-memsafety.i",
            #
            # "ldv-memsafety/memleaks_test19_false-valid-free.i",
            # "ldv-memsafety/memleaks_test11_2_false-valid-memtrack_true-termination.i",
            # "ldv-memsafety/memleaks_test6_3_false-valid-memtrack_true-termination.i",
            # "forester-heap/dll-queue_true-unreach-call_true-valid-memsafety.i",
            # "forester-heap/sll-rb-sentinel_true-unreach-call_true-valid-memsafety.i",
            #
            # "floats-esbmc-regression/floor_nondet_true-unreach-call.i",
            # "floats-esbmc-regression/isgreater_true-unreach-call.i",
            # "floats-esbmc-regression/round_nondet_true-unreach-call.i",
            #
            # "forester-heap/sll-token_true-unreach-call_true-valid-memsafety.i",
            # "list-ext2-properties/simple_search_value_true-unreach-call.i",
            # "ldv-sets/test_add_true-unreach-call_true-termination.i",
            #
            # "loop-lit/mcmillan2006_true-unreach-call_true-termination.c.i",
            #
            # "busybox-1.22.0/chgrp-incomplete_true-no-overflow_false-valid-memtrack.i",
            # "busybox-1.22.0/realpath_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/mkfifo-incomplete_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/uniq_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/basename_false-unreach-call_true-no-overflow_true-valid-memsafety.i",
            #
            # "busybox-1.22.0/logname_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/sync_true-no-overflow_true-valid-memsafety.i",
            # "busybox-1.22.0/usleep_true-no-overflow_true-valid-memsafety.i",

            # "pthread-C-DAC/pthread-demo-datarace_false-unreach-call.i",
            "pthread-complex/bounded_buffer_false-unreach-call.i",

            ]:
        if True: # Copy from repo to local evaluation dir
            os.makedirs(os.path.dirname(os.path.join(get_destination_root_dir(), bench_rpath)), exist_ok=True)
            shutil.copy(os.path.join(get_source_root_dir(), bench_rpath), os.path.join(get_destination_root_dir(), bench_rpath))
        else: # Copy back from local evaluation dir to repo
            shutil.copy(os.path.join(get_destination_root_dir(), bench_rpath), os.path.join(get_source_root_dir(), bench_rpath))


if __name__ == "__main__":
    exit(_main())
