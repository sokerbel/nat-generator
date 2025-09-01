#!/usr/bin/env python3
import streamlit as st
import ipaddress
import pandas as pd
import io

def generate_nat_mapping(dmz_range, internal_range):
    """Génère le mapping NAT 1:1 entre deux ranges IP"""
    try:
        # Créer les réseaux
        dmz_network = ipaddress.ip_network(dmz_range, strict=False)
        internal_network = ipaddress.ip_network(internal_range, strict=False)
        
        # Vérifier que les masques sont identiques
        if dmz_network.prefixlen != internal_network.prefixlen:
            return None, f"❌ ERREUR: Les masques doivent être identiques! DMZ: /{dmz_network.prefixlen}, Interne: /{internal_network.prefixlen}"
        
        # Générer les listes d'IPs
        dmz_ips = list(dmz_network.hosts())
        internal_ips = list(internal_network.hosts())
        
        # Si pas d'hôtes (petit réseau), prendre toutes les adresses
        if not dmz_ips:
            dmz_ips = list(dmz_network)
            internal_ips = list(internal_network)
        
        # Créer le mapping
        mappings = []
        for dmz_ip, internal_ip in zip(dmz_ips, internal_ips):
            mappings.append({
                'DMZ_IP': str(dmz_ip),
                'Internal_IP': str(internal_ip)
            })
        
        return mappings, None
        
    except ValueError as e:
        return None, f"❌ ERREUR: Format d'IP invalide - {e}"
    except Exception as e:
        return None, f"❌ ERREUR: {e}"

def main():
    # Page configuration
    st.set_page_config(
        page_title="1:1 NAT Generator",
        page_icon="🔧",
        layout="wide"
    )
    
    # Main title
    st.title("🔧 1:1 NAT TABLE GENERATOR")
    st.markdown("---")
    
    # Creator information
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 20px; padding: 10px; background-color: #f0f2f6; border-radius: 10px;'>
            <p style='margin: 0; color: #666;'>Created by <strong>Sofiane Kerbel</strong></p>
            <p style='margin: 5px 0 0 0;'><a href='https://www.linkedin.com/in/sofiane-kerbel' target='_blank'>🔗 LinkedIn Profile</a></p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("📍 IP Range Configuration")
        
        dmz_range = st.text_input(
            "DMZ Range",
            value="192.168.1.0/26",
            help="Format: IP/mask (e.g., 192.168.1.0/26)"
        )
        
        internal_range = st.text_input(
            "Internal Range", 
            value="10.188.65.0/26",
            help="Format: IP/mask (e.g., 10.188.65.0/26)"
        )
        
        generate_button = st.button("🚀 Generate Mapping", type="primary")
    
    # Main area
    if generate_button:
        if dmz_range and internal_range:
            with st.spinner("Generating mapping..."):
                mappings, error = generate_nat_mapping(dmz_range, internal_range)
            
            if error:
                st.error(error)
            else:
                # Display statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total Mappings", len(mappings))
                with col2:
                    st.metric("🌐 DMZ Range", dmz_range)
                with col3:
                    st.metric("🏠 Internal Range", internal_range)
                
                st.markdown("---")
                
                # Display table
                st.subheader("✅ 1:1 NAT MAPPING")
                df = pd.DataFrame(mappings)
                
                # Styled table display
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # CSV download button
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="💾 Download as CSV",
                    data=csv_data,
                    file_name="nat_mapping.csv",
                    mime="text/csv",
                    type="secondary"
                )
                
                # Network details display
                with st.expander("📋 Network Details"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**DMZ Range:**")
                        dmz_net = ipaddress.ip_network(dmz_range, strict=False)
                        st.write(f"- Network: {dmz_net.network_address}")
                        st.write(f"- Mask: /{dmz_net.prefixlen}")
                        st.write(f"- Broadcast: {dmz_net.broadcast_address}")
                        st.write(f"- Hosts: {dmz_net.num_addresses}")
                    
                    with col2:
                        st.write("**Internal Range:**")
                        int_net = ipaddress.ip_network(internal_range, strict=False)
                        st.write(f"- Network: {int_net.network_address}")
                        st.write(f"- Mask: /{int_net.prefixlen}")
                        st.write(f"- Broadcast: {int_net.broadcast_address}")
                        st.write(f"- Hosts: {int_net.num_addresses}")
        else:
            st.warning("⚠️ Please fill in both IP ranges")
    
    else:
        # Home page
        st.info("👈 Configure your IP ranges in the sidebar and click 'Generate Mapping'")
        
        # Examples
        st.subheader("📚 Usage Examples")
        
        examples = [
            {
                "Case": "Small network (/30)",
                "DMZ": "192.168.1.0/30", 
                "Internal": "10.0.1.0/30",
                "IPs": "2 usable addresses"
            },
            {
                "Case": "Medium network (/26)",
                "DMZ": "192.168.1.0/26",
                "Internal": "10.188.65.0/26", 
                "IPs": "62 usable addresses"
            },
            {
                "Case": "Large network (/24)",
                "DMZ": "192.168.1.0/24",
                "Internal": "10.0.1.0/24",
                "IPs": "254 usable addresses"
            }
        ]
        
        st.table(pd.DataFrame(examples))
        
        # Footer with creator info
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; margin-top: 30px; color: #888;'>
                <p>🛠️ Built by <strong><a href='https://www.linkedin.com/in/sofiane-kerbel' target='_blank'>Sofiane Kerbel</a></strong></p>
                <p style='font-size: 12px;'>Network Administration Tool | 1:1 NAT Mapping Generator</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()