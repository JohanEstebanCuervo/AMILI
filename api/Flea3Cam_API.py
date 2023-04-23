import PySpin as Ps


class Camera_PySpin(object):

    """docstring for Camera_PySpin"""

    def __init__(
        self,
        pyspin_camlis,
        Gamma=1.25,
        ExposureTime=8000,
        Gain=0,
        Sharpness=1800,
        BlackLevel=0.7,
        BufferMode="Continuous",
        BufferHandlingMode="NewestOnly",
        TriggerSource="Line2",
        BufferCount=8,
    ):
        try:
            self.__init_atributes()

            self.__cam = pyspin_camlis

            nodemap_tldevice = self.__cam.GetTLDeviceNodeMap()

            self.Device_Info(nodemap_tldevice)

            self.__cam.Init()

            self.__nodemap = self.__cam.GetNodeMap()

        except:
            print("Error en el inicio de la camara")

        if self.Set_Trigger_Mode(False):
            print("error set trigger mode configure")

        elif self.Set_Trigger_Source(TriggerSource):
            print("error set trigger source configure")

        elif self.Set_Trigger_Mode(True):
            print("error set trigger mode reconfigure ")

        elif self.Set_Gamma(Gamma):
            print("error set gamma configure")

        elif self.Set_BlackLevel(BlackLevel):
            print("error set black level configure")

        elif self.Set_Exposure_Auto(False):
            print("error set exposure auto configure")

        elif self.Set_Exposure(ExposureTime):
            print("error set exposure")

        elif self.Set_Gain_Auto(False):
            print("error set gain auto configure")

        elif self.Set_Gain(Gain):
            print("error set gain configure")

        elif self.Set_Sharpness_Auto(False):
            print("error set sharpness auto configure")

        elif self.Set_Sharpness(Sharpness):
            print("error set sharpness configure")

        elif self.Set_Buffer_Mode(BufferMode):
            print("error set buffer mode configure")

        elif self.Set_Buffer_Count(BufferCount):
            print("error set buffer count configure")

        elif self.Set_Buffer_Handling_Mode(BufferHandlingMode):
            print("error set buffer handling mode configure")

        else:
            print("camara iniciada corectamente")
            self.__init_complete = True

    def __init_atributes(self):
        self.__gamma = None
        self.__blacklevel = None
        self.__error_config = False
        self.__init_complete = False
        self.__trigger_mode = None
        self.__exposure_auto = None
        self.__exposure = None
        self.__gain_auto = None
        self.__gain = None
        self.__sharpness_auto = None
        self.__sharpness = None
        self.__buffer_mode = None
        self.__buffer_count = None
        self.__buffer_handling_mode = None
        self.__trigger_source = None

    ##################################
    # Device info
    ##################################

    def Device_Info(self, nodemap):
        try:
            nod_DI = Ps.CCategoryPtr(nodemap.GetNode("DeviceInformation"))
            self.__device_info = []

            if Ps.IsAvailable(nod_DI) and Ps.IsReadable(nod_DI):
                features = nod_DI.GetFeatures()

                for feature in features:
                    node_feature = Ps.CValuePtr(feature)
                    self.__device_info.append(
                        [
                            node_feature.GetName(),
                            node_feature.ToString()
                            if Ps.IsReadable(node_feature)
                            else "Node not readable",
                        ]
                    )

            else:
                print("Device control information not available.")

        except Ps.SpinnakerException as ex:
            print("Error: %s" % ex)

            if self.__init_complete is None:
                self.__init_complete = False

            else:
                self.__error_config = True

    ################################
    # Set Funcionts
    ################################

    def Set_BlackLevel(self, blacklevel):
        nod_BL = Ps.CFloatPtr(self.__nodemap.GetNode("BlackLevel"))

        if not Ps.IsAvailable(nod_BL) or not Ps.IsWritable(nod_BL):
            print("Unable to set BlackLevel (float retrieval). Aborting...\n")

            if self.__init_complete is None:
                self.__init_complete = False

            else:
                self.__error_config = True

            return 1

        nod_BL.SetValue(blacklevel)

        self.__blacklevel = blacklevel

        return 0

    def Set_Gamma(self, gamma):
        node_Gamma = Ps.CFloatPtr(self.__nodemap.GetNode("Gamma"))

        if not Ps.IsAvailable(node_Gamma) or not Ps.IsWritable(node_Gamma):
            print("Unable to set Gamma Time (Integer retrieval). Aborting...")

            if self.__init_complete is None:
                self.__init_complete = False

            else:
                self.__error_config = True

            return 1

        node_Gamma.SetValue(gamma)

        self.__gamma = gamma

        return 0

    def Set_Gain(self, gain):
        node_Gain = Ps.CFloatPtr(self.__nodemap.GetNode("Gain"))

        if not Ps.IsAvailable(node_Gain) or not Ps.IsWritable(node_Gain):
            print("\nUnable to set Gain (float retrieval). Aborting...\n")

            if self.__init_complete is None:
                self.__init_complete = False

            else:
                self.__error_config = True

            return 1

        node_Gain.SetValue(gain)

        self.__gain = gain

        return 0

    def Set_Sharpness(self, sharpness):
        nod_Sh = Ps.CIntegerPtr(self.__nodemap.GetNode("Sharpness"))

        if not Ps.IsAvailable(nod_Sh) or not Ps.IsWritable(nod_Sh):
            print("\nUnable to set Sharpness Time (Integer retrieval). Aborting...\n")

            if self.__init_complete is None:
                self.__init_complete = False

            else:
                self.__error_config = True

            return 1

        nod_Sh.SetValue(sharpness)

        self.__sharpness = sharpness

        return 0

    def Set_Exposure(self, exposure):
        if self.__cam.ExposureTime.GetAccessMode() != Ps.RW:
            print("Unable to set exposure time. Aborting...")
            return 1

        # Ensure desired exposure time does not exceed the maximum

        exposure_time_to_set = min(self.__cam.ExposureTime.GetMax(), exposure)

        # self.__cam.ExposureTime.SetValue(exposure_time_to_set)
        self.__cam.ExposureMode.SetValue(1)
        self.__exposure = exposure

        return 0

    def Set_Gain_Auto(self, boolean):
        if boolean == self.__gain_auto:
            return 0

        nod_GA = Ps.CEnumerationPtr(self.__nodemap.GetNode("GainAuto"))

        if not Ps.IsAvailable(nod_GA) or not Ps.IsWritable(nod_GA):
            print("\nUnable to set Gain Auto (enumeration retrieval). Aborting...\n")

            if self.__init_complete is None:
                self.__init_complete = False

            else:
                self.__error_config = True

            return 1

        if boolean:
            ent_GA_on = nod_GA.GetEntryByName("Continuous")

            if not Ps.IsAvailable(ent_GA_on) or not Ps.IsReadable(ent_GA_on):
                print("\nUnable to set Gain Auto (entry retrieval). Aborting...\n")

                if self.__init_complete is None:
                    self.__init_complete = False

                else:
                    self.__error_config = True

                return 1

            gain_auto_on = ent_GA_on.GetValue()

            nod_GA.SetIntValue(gain_auto_on)

        else:
            ent_GA_off = nod_GA.GetEntryByName("Off")

            if not Ps.IsAvailable(ent_GA_off) or not Ps.IsReadable(ent_GA_off):
                print("\nUnable to set Gain Auto (entry retrieval). Aborting...\n")

                if self.__init_complete is None:
                    self.__init_complete = False

                else:
                    self.__error_config = True

                return 1

            gain_auto_off = ent_GA_off.GetValue()

            nod_GA.SetIntValue(gain_auto_off)

        self.__gain_auto = boolean

        return 0

    def Set_Exposure_Auto(self, boolean):
        if boolean == self.__exposure_auto:
            return 0

        trigger_mode = self.__trigger_mode

        if trigger_mode:
            self.Set_Trigger_Mode(False)

        if self.__cam.ExposureAuto.GetAccessMode() != Ps.RW:
            print("Unable to disable automatic exposure. Aborting...")

            if self.__init_complete is None:
                self.__init_complete = False

            else:
                self.__error_config = True

            return 1

        if boolean:
            self.__cam.ExposureAuto.SetValue(Ps.ExposureAuto_Continuous)

        else:
            self.__cam.ExposureAuto.SetValue(Ps.ExposureAuto_Off)

        self.__exposure_auto = boolean

        if trigger_mode:
            self.Set_Trigger_Mode(True)

        return 0

    def Set_Sharpness_Auto(self, boolean):
        if boolean == self.__sharpness_auto:
            return 0

        nod_SA = Ps.CEnumerationPtr(self.__nodemap.GetNode("SharpnessAuto"))

        if not Ps.IsAvailable(nod_SA) or not Ps.IsWritable(nod_SA):
            print(
                "\nUnable to set Sharpness Auto (enumeration retrieval). Aborting...\n"
            )

            if self.__init_complete is None:
                self.__init_complete = False

            else:
                self.__error_config = True

            return 1

        if boolean:
            ent_SA_on = nod_SA.GetEntryByName("Continuous")
            if not Ps.IsAvailable(ent_SA_on) or not Ps.IsReadable(ent_SA_on):
                print("\nUnable to set Sharpness Auto (entry retrieval). Aborting...\n")

                if self.__init_complete is None:
                    self.__init_complete = False

                else:
                    self.__error_config = True

                return 1

            Sharpness_auto_on = ent_SA_on.GetValue()

            nod_SA.SetIntValue(Sharpness_auto_on)

        else:
            ent_SA_off = nod_SA.GetEntryByName("Off")
            if not Ps.IsAvailable(ent_SA_off) or not Ps.IsReadable(ent_SA_off):
                print("\nUnable to set Sharpness Auto (entry retrieval). Aborting...\n")

                if self.__init_complete is None:
                    self.__init_complete = False

                else:
                    self.__error_config = True

                return 1

            Sharpness_auto_off = ent_SA_off.GetValue()

            nod_SA.SetIntValue(Sharpness_auto_off)

        self.__sharpness_auto = boolean

        return 0

    def Set_Trigger_Mode(self, boolean):
        if boolean == self.__trigger_mode:
            return 0

        if self.__cam.TriggerMode.GetAccessMode() != Ps.RW:
            print("Unable to disable trigger mode (node retrieval). Aborting.")

            if self.__init_complete is None:
                self.__init_complete = False

            else:
                self.__error_config = True

            return 1

        if boolean:
            self.__cam.TriggerMode.SetValue(Ps.TriggerMode_On)
            self.__cam.TriggerActivation.SetValue(Ps.TriggerActivation_RisingEdge)

        else:
            self.__cam.TriggerMode.SetValue(Ps.TriggerMode_Off)

        if boolean:
            print("Activado el trigger")

        else:
            print("desactivado el trigger")

        self.__trigger_mode = boolean

        return 0

    def Set_Trigger_Source(self, line):
        trigger_mode = self.__trigger_mode
        if trigger_mode:
            self.Set_Trigger_Mode(False)

        if self.__cam.TriggerSource.GetAccessMode() != Ps.RW:
            print("Unable to get trigger source (node retrieval). Aborting...")
            if self.__init_complete is None:
                self.__init_complete = False

            else:
                self.__error_config = True

            return 1

        self.__cam.TriggerSource.SetValue(Ps.TriggerSelector_FrameStart)

        if line == "Software":
            self.__cam.TriggerSource.SetValue(Ps.TriggerSource_Software)

        elif line == "Line0":
            self.__cam.TriggerSource.SetValue(Ps.TriggerSource_Line0)

        elif line == "Line1":
            self.__cam.TriggerSource.SetValue(Ps.TriggerSource_Line1)

        elif line == "Line2":
            self.__cam.TriggerSource.SetValue(Ps.TriggerSource_Line2)

        else:
            print("Trigger Source Invalid")
            return 1

        self.__trigger_source = line

        if trigger_mode:
            self.Set_Trigger_Mode(True)

        return 0

    def Set_Buffer_Mode(self, mode):
        if self.__cam.AcquisitionMode.GetAccessMode() != Ps.RW:
            print("Unable to disable acquisition mode. Aborting...")

            if self.__init_complete is None:
                self.__init_complete = False

            else:
                self.__error_config = True

            return 1

        if mode == "Continuous":
            self.__cam.AcquisitionMode.SetValue(Ps.AcquisitionMode_Continuous)

        elif mode == "SingleFrame":
            self.__cam.AcquisitionMode.SetValue(Ps.AcquisitionMode_SingleFrame)

        elif mode == "MultiFrame":
            self.__cam.AcquisitionMode.SetValue(Ps.AcquisitionMode_MultiFrame)

        else:
            print("Buffer Mode Invalid")
            return 1

        self.__buffer_mode = mode

        return 0

    def Set_Buffer_Count(self, numbuffer):
        nod_stream = self.__cam.GetTLStreamNodeMap()
        stream_BCM = Ps.CEnumerationPtr(nod_stream.GetNode("StreamBufferCountMode"))

        if not Ps.IsAvailable(stream_BCM) or not Ps.IsWritable(stream_BCM):
            print("Unable to set Buffer Count Mode (node retrieval). Aborting...\n")
            return 1

        stream_BCM_m = Ps.CEnumEntryPtr(stream_BCM.GetEntryByName("Manual"))

        if not Ps.IsAvailable(stream_BCM_m) or not Ps.IsReadable(stream_BCM_m):
            print(
                "Unable to set Buffer Count Mode entry (Entry retrieval). Aborting...\n"
            )
            return 1

        stream_BCM.SetIntValue(stream_BCM_m.GetValue())

        # Retrieve and modify Stream Buffer Count
        buffer_count = Ps.CIntegerPtr(nod_stream.GetNode("StreamBufferCountManual"))
        if not Ps.IsAvailable(buffer_count) or not Ps.IsWritable(buffer_count):
            print("Unable to set Buffer Count (Integer node retrieval). Aborting...\n")

            if self.__init_complete is None:
                self.__init_complete = False

            else:
                self.__error_config = True

            return 1

        # No exceder el maximo de buffer
        numbuffer = min(buffer_count.GetMax(), numbuffer)

        buffer_count.SetValue(numbuffer)

        self.__buffer_count = numbuffer

        return 0

    def Set_Buffer_Handling_Mode(self, mode):
        nod_stream = self.__cam.GetTLStreamNodeMap()

        handling_mode = Ps.CEnumerationPtr(
            nod_stream.GetNode("StreamBufferHandlingMode")
        )

        if not Ps.IsAvailable(handling_mode) or not Ps.IsWritable(handling_mode):
            print("Unable to set Buffer Handling mode (node retrieval). Aborting...\n")
            if self.__init_complete is None:
                self.__init_complete = False

            else:
                self.__error_config = True

            return 1

        handling_mode_entry = Ps.CEnumEntryPtr(handling_mode.GetCurrentEntry())

        if not Ps.IsAvailable(handling_mode_entry) or not Ps.IsReadable(
            handling_mode_entry
        ):
            print("Unable to set Buffer Handling mode (Entry retrieval). Aborting...\n")
            if self.__init_complete is None:
                self.__init_complete = False

            else:
                self.__error_config = True

            return 1

        if (
            mode == "NewestFirst"
            or mode == "NewestOnly"
            or mode == "OldestFirst"
            or mode == "OldestFirstOverwrite"
        ):
            handling_mode_entry = handling_mode.GetEntryByName(mode)
            handling_mode.SetIntValue(handling_mode_entry.GetValue())

        else:
            print("buffer handling mode invalid")
            return 1

        self.__buffer_handling_mode = mode

        return 0

    #############################################
    # Mode Functions
    ############################################
    def Mode_Acquisition_Multispectral(self):
        self.Set_Gain_Auto(False)
        self.Set_Gain(self.__gain)
        self.Set_Sharpness_Auto(False)
        self.Set_Sharpness(self.__sharpness)
        self.Set_Exposure_Auto(False)
        self.Set_Exposure(self.__exposure)

        self.Set_Trigger_Mode(True)

    def Mode_Acquisition_Video(self):
        self.Set_Gain_Auto(True)
        self.Set_Sharpness_Auto(True)
        self.Set_Exposure_Auto(True)
        self.Set_Trigger_Mode(False)

    def Acquire_Image(self, nombre):
        image_result = self.__cam.GetNextImage(1000)

        if image_result.IsIncomplete():
            print(
                "Image incomplete with image status %d ..."
                % image_result.GetImageStatus()
            )

        else:
            image_converted = image_result.Convert(Ps.PixelFormat_Mono8, Ps.HQ_LINEAR)

            filename = "temp/" + nombre + ".bmp"

            image_converted.Save(filename)

            image_result.Release()

    def Init_Acquisition(self):
        self.__cam.BeginAcquisition()

    def End_Acquisition(self):
        self.__cam.EndAcquisition()

    ###################################
    # Get Funcitons
    ###################################

    def get_device_info(self):
        return self.__device_info

    def get_init_complete(self):
        return self.__init_complete

    def get_error_config(self):
        return self.__error_config

    def get_trigger_mode(self):
        return self.__trigger_mode

    def get_exposure_auto(self):
        return self.__exposure_auto

    def get_gain_auto(self):
        return self.__gain_auto

    def get_sharpness_auto(self):
        return self.__sharpness_auto

    def get_trigger_source(self):
        return self.__trigger_source

    def get_buffer_mode(self):
        return self.__buffer_mode

    def get_buffer_count(self):
        return self.__buffer_count

    def get_buffer_handling_mode(self):
        return self.__buffer_handling_mode

    def get_gain(self):
        return self.__gain

    def get_blacklevel(self):
        return self.__blacklevel

    def get_sharpness(self):
        return self.__sharpness

    def get_gamma(self):
        return self.__gamma

    def get_exposure(self):
        return self.__exposure

    ##################################
    # Special Functions
    ################################

    def Reset(self):
        # presenta error en spinnakker #
        return self.__cam.DeviceReset.Execute()

    def __del__(self):
        self.Mode_Acquisition_Video()

        self.__cam.DeInit()
