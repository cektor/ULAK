package com.ulak

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.net.wifi.p2p.*
import android.os.Build
import android.util.Log
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

data class WifiDirectDevice(
    val name: String,
    val address: String,
    val status: Int
)

class WifiDirectManager(private val context: Context) {
    
    companion object {
        private const val TAG = "WifiDirectManager"
    }
    
    private val wifiP2pManager: WifiP2pManager? = context.getSystemService(Context.WIFI_P2P_SERVICE) as? WifiP2pManager
    private var channel: WifiP2pManager.Channel? = null
    
    private val _discoveredDevices = MutableStateFlow<List<WifiDirectDevice>>(emptyList())
    val discoveredDevices: StateFlow<List<WifiDirectDevice>> = _discoveredDevices
    
    private val _isConnected = MutableStateFlow(false)
    val isConnected: StateFlow<Boolean> = _isConnected
    
    private val _connectionInfo = MutableStateFlow<WifiP2pInfo?>(null)
    val connectionInfo: StateFlow<WifiP2pInfo?> = _connectionInfo
    
    private val peers = mutableListOf<WifiP2pDevice>()
    
    var onConnectionChanged: ((Boolean, String?) -> Unit)? = null
    
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            when (intent.action) {
                WifiP2pManager.WIFI_P2P_STATE_CHANGED_ACTION -> {
                    val state = intent.getIntExtra(WifiP2pManager.EXTRA_WIFI_STATE, -1)
                    val isEnabled = state == WifiP2pManager.WIFI_P2P_STATE_ENABLED
                    Log.d(TAG, "Wi-Fi P2P state: $isEnabled")
                }
                
                WifiP2pManager.WIFI_P2P_PEERS_CHANGED_ACTION -> {
                    wifiP2pManager?.requestPeers(channel) { peerList ->
                        peers.clear()
                        peers.addAll(peerList.deviceList)
                        
                        val devices = peers.map { device ->
                            WifiDirectDevice(
                                name = device.deviceName,
                                address = device.deviceAddress,
                                status = device.status
                            )
                        }
                        _discoveredDevices.value = devices
                        Log.d(TAG, "Peers updated: ${devices.size} devices")
                    }
                }
                
                WifiP2pManager.WIFI_P2P_CONNECTION_CHANGED_ACTION -> {
                    wifiP2pManager?.requestConnectionInfo(channel) { info ->
                        _connectionInfo.value = info
                        _isConnected.value = info.groupFormed
                        
                        if (info.groupFormed) {
                            val groupOwnerIp = info.groupOwnerAddress.hostAddress
                            val localIp = getLocalIpAddress()
                            val isOwner = info.isGroupOwner
                            
                            Log.d(TAG, "Connected - Group Owner: $isOwner")
                            Log.d(TAG, "Group Owner IP: $groupOwnerIp")
                            Log.d(TAG, "Local IP: $localIp")
                            
                            // Karşı cihaza gönderirken kullanılacak IP
                            val targetIp = if (isOwner) {
                                // Biz owner'sak, client'a göndereceğiz ama client IP'sini bilmiyoruz
                                // Client bize bağlanır, biz dinleriz
                                localIp
                            } else {
                                // Biz client'sak, owner'a göndereceğiz
                                groupOwnerIp
                            }
                            
                            Log.d(TAG, "Target IP for sending: $targetIp")
                            onConnectionChanged?.invoke(true, targetIp)
                        } else {
                            Log.d(TAG, "Disconnected")
                            onConnectionChanged?.invoke(false, null)
                        }
                    }
                }
                
                WifiP2pManager.WIFI_P2P_THIS_DEVICE_CHANGED_ACTION -> {
                    val device = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                        intent.getParcelableExtra(WifiP2pManager.EXTRA_WIFI_P2P_DEVICE, WifiP2pDevice::class.java)
                    } else {
                        @Suppress("DEPRECATION")
                        intent.getParcelableExtra(WifiP2pManager.EXTRA_WIFI_P2P_DEVICE)
                    }
                    Log.d(TAG, "This device: ${device?.deviceName}")
                }
            }
        }
    }
    
    fun initialize() {
        channel = wifiP2pManager?.initialize(context, context.mainLooper, null)
        
        val intentFilter = IntentFilter().apply {
            addAction(WifiP2pManager.WIFI_P2P_STATE_CHANGED_ACTION)
            addAction(WifiP2pManager.WIFI_P2P_PEERS_CHANGED_ACTION)
            addAction(WifiP2pManager.WIFI_P2P_CONNECTION_CHANGED_ACTION)
            addAction(WifiP2pManager.WIFI_P2P_THIS_DEVICE_CHANGED_ACTION)
        }
        
        context.registerReceiver(receiver, intentFilter)
        Log.d(TAG, "Wi-Fi Direct initialized")
    }
    
    fun startDiscovery() {
        wifiP2pManager?.discoverPeers(channel, object : WifiP2pManager.ActionListener {
            override fun onSuccess() {
                Log.d(TAG, "Discovery started")
            }
            
            override fun onFailure(reason: Int) {
                Log.e(TAG, "Discovery failed: $reason")
            }
        })
    }
    
    fun stopDiscovery() {
        wifiP2pManager?.stopPeerDiscovery(channel, object : WifiP2pManager.ActionListener {
            override fun onSuccess() {
                Log.d(TAG, "Discovery stopped")
            }
            
            override fun onFailure(reason: Int) {
                Log.e(TAG, "Stop discovery failed: $reason")
            }
        })
    }
    
    fun connect(deviceAddress: String, onResult: (Boolean, String?) -> Unit) {
        val config = WifiP2pConfig().apply {
            this.deviceAddress = deviceAddress
            groupOwnerIntent = 0 // Auto-select group owner
        }
        
        wifiP2pManager?.connect(channel, config, object : WifiP2pManager.ActionListener {
            override fun onSuccess() {
                Log.d(TAG, "Connection initiated to $deviceAddress")
                onResult(true, null)
            }
            
            override fun onFailure(reason: Int) {
                val error = when (reason) {
                    WifiP2pManager.P2P_UNSUPPORTED -> "Wi-Fi Direct desteklenmiyor"
                    WifiP2pManager.ERROR -> "Bağlantı hatası"
                    WifiP2pManager.BUSY -> "Sistem meşgul"
                    else -> "Bilinmeyen hata: $reason"
                }
                Log.e(TAG, "Connection failed: $error")
                onResult(false, error)
            }
        })
    }
    
    fun disconnect() {
        wifiP2pManager?.removeGroup(channel, object : WifiP2pManager.ActionListener {
            override fun onSuccess() {
                Log.d(TAG, "Disconnected")
                _isConnected.value = false
                _connectionInfo.value = null
            }
            
            override fun onFailure(reason: Int) {
                Log.e(TAG, "Disconnect failed: $reason")
            }
        })
    }
    
    fun cleanup() {
        try {
            context.unregisterReceiver(receiver)
        } catch (e: Exception) {
            Log.e(TAG, "Cleanup error", e)
        }
        disconnect()
        channel?.close()
    }
    
    private fun getLocalIpAddress(): String? {
        try {
            val interfaces = java.net.NetworkInterface.getNetworkInterfaces()
            while (interfaces.hasMoreElements()) {
                val intf = interfaces.nextElement()
                if (intf.name.startsWith("p2p")) {
                    val addrs = intf.inetAddresses
                    while (addrs.hasMoreElements()) {
                        val addr = addrs.nextElement()
                        if (!addr.isLoopbackAddress && addr is java.net.Inet4Address) {
                            return addr.hostAddress
                        }
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error getting local IP", e)
        }
        return null
    }
    
    fun getGroupOwnerAddress(): String? {
        val info = _connectionInfo.value ?: return null
        return if (info.isGroupOwner) {
            // Biz Group Owner'sak, client'a göndereceğiz
            // Client genellikle 192.168.49.x ağında olur
            null // Client IP'sini bulamayız, karşı taraf bize bağlanır
        } else {
            // Biz client'sak, Group Owner'a göndereceğiz
            info.groupOwnerAddress.hostAddress
        }
    }
    
    fun isGroupOwner(): Boolean {
        return _connectionInfo.value?.isGroupOwner ?: false
    }
}
