<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" />
  <xsl:template match="/">
    <!-- <xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;</xsl:text> -->
    <html>
      <head>
        <title>Data Analysis</title>
        <link rel="stylesheet" type="text/css" href="templates/styles.css" />
        <meta http-equiv="X-UA-Compatible" content="IE=11,chrome=1" />
        <meta http-equiv="pragma" content="no-cache" />
        <script>
          function deleteAll() {
            var hideRows = document.querySelectorAll('.hide');
            for (var i = 0; i &lt; hideRows.length; ++i) {
                hideRows[i].parentNode.removeChild(hideRows[i]);
            }
            var hideButton = document.getElementById('toggle-hide');
            hideButton.style.display = 'none';
          }
        </script>
      </head>

      <body>
        <button id="toggle-hide" onclick="deleteAll()">Hide Stats</button>
        <!-- Main Header -->
        <h1><div contenteditable="true"><xsl:value-of select="test/@name"/></div></h1>
        
        <!-- Time Analysis -->
        <h3>Data analysis as of <xsl:value-of select="test/time/timestamp"/></h3>

        <!-- Profile Analysis -->
        <table>
          <tr bgcolor="e3e3e3">
            <th>Thermocouple</th>
            <th>Min (°C)</th>
            <th>Max (°C)</th>
          </tr>
          <xsl:for-each select="test/profile/thermocouple">
            <tr>
              <td><xsl:value-of select="name"/></td>
              <td><xsl:value-of select="temp-min"/></td>
              <td><xsl:value-of select="temp-max"/></td>
            </tr>
          </xsl:for-each>
        </table>

        <!-- TEMPERATURE -->
        <xsl:for-each select="test/temperature">
          <br/><hr/>
          <h2><div contenteditable="true"><xsl:value-of select="@temp"/></div></h2>
      
          <!-- MODE -->
          <xsl:for-each select="mode">

            <table border="1">
              <!-- Test Name Header -->
              <tr bgcolor="#989898">
                <th>
                  <xsl:attribute name="colspan"><xsl:value-of select="@width"/></xsl:attribute>
                  <div contenteditable="true"><xsl:value-of select="../../@name"/></div>
                </th>
              </tr>

              <!-- Mode Temperature Header -->
              <tr>
                <xsl:attribute name="class"><xsl:value-of select="@id"/></xsl:attribute>
                <th>
                  <xsl:attribute name="colspan"><xsl:value-of select="@width"/></xsl:attribute>
                  <div contenteditable="true">
                    <xsl:value-of select="@id"/> at <xsl:value-of select="../@temp"/>
                  </div>
                </th>
              </tr>
              <xsl:for-each select="voltage">

                <!-- Voltage Header -->
                <tr bgcolor="#d3d3d3">
                  <th>
                    <xsl:attribute name="colspan"><xsl:value-of select="@width"/></xsl:attribute>
                    <div contenteditable="true"><xsl:value-of select="@value"/></div>
                  </th>
                </tr>

                <!-- Limits Header -->
                <xsl:choose>
                  <xsl:when test="limits">
                    <tr bgcolor="#d3d3d3">
                      <th>
                        <xsl:attribute name="colspan"><xsl:value-of select="@width"/></xsl:attribute>
                        <div contenteditable="true"><xsl:value-of select="limits"/></div>
                      </th>
                    </tr>
                   </xsl:when>
                </xsl:choose>

                <!-- Names -->
                <tr bgcolor="#d3d3d3">
                  <th><div contenteditable="true">Name:</div></th>
                  <xsl:for-each select="vsenses/vsense">
                    <td align="center"><div contenteditable="true"><xsl:value-of select="name"/></div></td>
                  </xsl:for-each>
                  <xsl:for-each select="systems/system">
                    <td align="center"><div contenteditable="true"><xsl:value-of select="name"/></div></td>
                  </xsl:for-each>
                </tr>

                <!-- Minimums -->
                <tr>
                  <th><div contenteditable="true">Min:</div></th>
                  <xsl:for-each select="vsenses/vsense">
                    <td align="center"><xsl:value-of select="min"/></td>
                  </xsl:for-each>
                  <xsl:for-each select="systems/system">
                    <td align="center"><xsl:value-of select="min"/></td>
                  </xsl:for-each>
                </tr>

                <!-- Maximums -->
                <tr>
                  <th><div contenteditable="true">Max:</div></th>
                  <xsl:for-each select="vsenses/vsense">
                    <td align="center"><xsl:value-of select="max"/></td>
                  </xsl:for-each>
                  <xsl:for-each select="systems/system">
                    <td align="center"><xsl:value-of select="max"/></td>
                  </xsl:for-each>
                </tr>

                <!-- Averages -->
                <tr class="hide">
                  <th><div contenteditable="true">Avg:</div></th>
                  <xsl:for-each select="vsenses/vsense">
                    <td align="center"><xsl:value-of select="mean"/></td>
                  </xsl:for-each>
                  <xsl:for-each select="systems/system">
                    <td align="center"><xsl:value-of select="mean"/></td>
                  </xsl:for-each>
                </tr>              

                <!-- Standard Deviations -->
                <tr class="hide">
                  <th><div contenteditable="true">St dev:</div></th>
                  <xsl:for-each select="vsenses/vsense">
                    <td align="center"><xsl:value-of select="std"/></td>
                  </xsl:for-each>
                  <xsl:for-each select="systems/system">
                    <td align="center"><xsl:value-of select="std"/></td>
                  </xsl:for-each>
                </tr>   

                <!-- Count Total -->
                <tr class="hide">
                  <th><div contenteditable="true">Total Count:</div></th>
                  <xsl:for-each select="vsenses/vsense">
                    <td align="center"><xsl:value-of select="count"/></td>
                  </xsl:for-each>
                  <xsl:for-each select="systems/system">
                    <td align="center"><xsl:value-of select="count"/></td>
                  </xsl:for-each>
                </tr>

                <!-- Count Out of Spec -->
                <tr class="hide">
                  <th><div contenteditable="true">Count Out:</div></th>
                  <xsl:for-each select="vsenses/vsense">
                    <td align="center"><xsl:value-of select="count-out"/></td>
                  </xsl:for-each>
                  <xsl:for-each select="systems/system">
                    <td align="center"><xsl:value-of select="count-out"/></td>
                  </xsl:for-each>
                </tr>

                <!-- Percent Out -->
                <tr class="hide">
                  <th><div contenteditable="true">Percent Out:</div></th>
                  <xsl:for-each select="vsenses/vsense">
                    <td align="center"><xsl:value-of select="percent-out"/></td>
                  </xsl:for-each>
                  <xsl:for-each select="systems/system">
                    <td align="center"><xsl:value-of select="percent-out"/></td>
                  </xsl:for-each>
                </tr>

                <!-- Multimode Ratios -->
                <xsl:if test="systems/system/board_min1">
                  <tr class="hide">
                    <th><div contenteditable="true"><xsl:value-of select="systems/system/board_min1/@id"/> Min:</div></th>
                    <xsl:for-each select="vsenses/vsense">
                      <td align="center"></td>
                    </xsl:for-each>
                    <xsl:for-each select="systems/system">
                      <td align="center"><xsl:value-of select="board_min1"/></td>
                    </xsl:for-each>
                  </tr>
                  <tr class="hide">
                    <th><div contenteditable="true"><xsl:value-of select="systems/system/board_min2/@id"/> Min:</div></th>
                    <xsl:for-each select="vsenses/vsense">
                      <td align="center"></td>
                    </xsl:for-each>
                    <xsl:for-each select="systems/system">
                      <td align="center"><xsl:value-of select="board_min2"/></td>
                    </xsl:for-each>
                  </tr>
                  <tr class="hide">
                    <th><div contenteditable="true"><xsl:value-of select="systems/system/board_max1/@id"/> Max:</div></th>
                    <xsl:for-each select="vsenses/vsense">
                      <td align="center"></td>
                    </xsl:for-each>
                    <xsl:for-each select="systems/system">
                      <td align="center"><xsl:value-of select="board_max1"/></td>
                    </xsl:for-each>
                  </tr>
                  <tr class="hide">
                    <th><div contenteditable="true"><xsl:value-of select="systems/system/board_max2/@id"/> Max:</div></th>
                    <xsl:for-each select="vsenses/vsense">
                      <td align="center"></td>
                    </xsl:for-each>
                    <xsl:for-each select="systems/system">
                      <td align="center"><xsl:value-of select="board_max2"/></td>
                    </xsl:for-each>
                  </tr>
                </xsl:if>
                              
                <!-- Check Data -->
                <tr>
                  <th><div contenteditable="true">Check Data:</div></th>
                  <xsl:for-each select="vsenses/vsense">
                    <xsl:choose>
                      <xsl:when test="check = 'Out of Spec'">
                        <td bgcolor="yellow" align="center"><xsl:value-of select="check"/></td>
                      </xsl:when>
                      <xsl:otherwise>
                        <td align="center"><xsl:value-of select="check"/></td>
                      </xsl:otherwise>
                    </xsl:choose>
                  </xsl:for-each>
                  <xsl:for-each select="systems/system">
                    <xsl:choose>
                      <xsl:when test="check = 'Out of Spec'">
                        <td bgcolor="yellow" align="center"><xsl:value-of select="check"/></td>
                      </xsl:when>
                      <xsl:when test="check = 'NA'">
                        <td bgcolor="gainsboro" align="center"><xsl:value-of select="check"/></td>
                      </xsl:when>
                      <xsl:otherwise>
                        <td align="center"><xsl:value-of select="check"/></td>
                      </xsl:otherwise>
                    </xsl:choose>
                  </xsl:for-each>
                </tr>

              </xsl:for-each><!-- end voltage -->
            </table>
            <br/><br/>

          </xsl:for-each><!-- end mode -->


          <!-- OUTAGE -->
          <xsl:for-each select="outages/outage">
            <table border="1">
              <!-- Test Name Header -->
              <tr bgcolor="#989898">
                <th>
                  <xsl:attribute name="colspan"><xsl:value-of select="@width"/></xsl:attribute>
                  <div contenteditable="true"><xsl:value-of select="../../../@name"/></div>
                </th>
              </tr>

              <!-- Outage Header -->
              <tr>
                <th class="OUTAGE">
                  <xsl:attribute name="colspan"><xsl:value-of select="@width"/></xsl:attribute>
                  <div contenteditable="true">
                    <xsl:value-of select="@id"/> at <xsl:value-of select="../../@temp"/>
                  </div>
                </th>
              </tr>
              <xsl:for-each select="voltage">

                <!-- Outage Voltage Header -->
                <tr bgcolor="#d3d3d3">
                  <th>
                    <xsl:attribute name="colspan"><xsl:value-of select="@width"/></xsl:attribute>
                    <div contenteditable="true"><xsl:value-of select="@value"/></div>
                  </th>
                </tr>

                <!-- Outage Limits Header -->
                <xsl:choose>
                  <xsl:when test="limits">
                    <tr bgcolor="#d3d3d3">
                      <th>
                        <xsl:attribute name="colspan"><xsl:value-of select="@width"/></xsl:attribute>
                        <div contenteditable="true"><xsl:value-of select="limits"/></div>
                      </th>
                    </tr>
                   </xsl:when>
                </xsl:choose>

                <!-- Outage System Names -->
                <tr bgcolor="#d3d3d3">
                  <th><div contenteditable="true">Name:</div></th>
                  <xsl:for-each select="systems/system">
                    <td align="center"><div contenteditable="true"><xsl:value-of select="name"/></div></td>
                  </xsl:for-each>
                </tr>

                <!-- Outage Minimums -->
                <tr>
                  <th><div contenteditable="true">Min:</div></th>
                  <xsl:for-each select="systems/system">
                    <td align="center"><xsl:value-of select="min"/></td>
                  </xsl:for-each>
                </tr>

                <!-- Outage Maximums -->
                <tr>
                  <th><div contenteditable="true">Max:</div></th>
                  <xsl:for-each select="systems/system">
                    <td align="center"><xsl:value-of select="max"/></td>
                  </xsl:for-each>
                </tr>

                <!-- Outage Averages -->
                <tr class="hide">
                  <th><div contenteditable="true">Avg:</div></th>
                  <xsl:for-each select="systems/system">
                    <td align="center"><xsl:value-of select="mean"/></td>
                  </xsl:for-each>
                </tr> 

                <!-- Outage Standard Deviations -->
                <tr class="hide">
                  <th><div contenteditable="true">St dev:</div></th>
                  <xsl:for-each select="systems/system">
                    <td align="center"><xsl:value-of select="std"/></td>
                  </xsl:for-each>
                </tr> 

                <!-- Outage Count Total -->
                <tr class="hide">
                  <th><div contenteditable="true">Total Count:</div></th>
                  <xsl:for-each select="systems/system">
                    <td align="center"><xsl:value-of select="count"/></td>
                  </xsl:for-each>
                </tr>

                <!-- Outage Count Out of Spec -->
                <tr class="hide">
                  <th><div contenteditable="true">Count Out:</div></th>
                  <xsl:for-each select="systems/system">
                    <td align="center"><xsl:value-of select="count-out"/></td>
                  </xsl:for-each>
                </tr>

                <!-- Outage Percent Out -->
                <tr class="hide">
                  <th><div contenteditable="true">Percent Out:</div></th>
                  <xsl:for-each select="systems/system">
                    <td align="center"><xsl:value-of select="percent-out"/></td>
                  </xsl:for-each>
                </tr> 

                <!-- Outage Check Data -->
                <tr>
                  <th><div contenteditable="true">Check Data:</div></th>
                  <xsl:for-each select="systems/system">
                    <xsl:choose>
                      <xsl:when test="check = 'Out of Spec'">
                        <td bgcolor="yellow" align="center"><xsl:value-of select="check"/></td>
                      </xsl:when>
                      <xsl:when test="check = 'NA'">
                        <td bgcolor="gainsboro" align="center"><xsl:value-of select="check"/></td>
                      </xsl:when>
                      <xsl:otherwise>
                        <td align="center"><xsl:value-of select="check"/></td>
                      </xsl:otherwise>
                    </xsl:choose>
                  </xsl:for-each>
                </tr>

              </xsl:for-each>
            </table><!-- end outage table -->
            <br/><br/>
          </xsl:for-each><!-- end of outages -->

          <br/><br/><br/>
        </xsl:for-each><!-- end temperature -->


        <!-- USER INPUTS -->
        <hr/>
        <h2>User Inputs</h2>
        <ul>
          <li><strong>Test Name:  </strong><xsl:value-of select="test/user-inputs/test-name"/></li>
          <li><strong>Data Folder:  </strong><xsl:value-of select="test/user-inputs/folder"/></li>
          <li><strong>DUTs:  </strong><xsl:value-of select="test/user-inputs/systems"/></li>
          <li><strong>Limits File:  </strong><xsl:value-of select="test/user-inputs/limits-file"/></li>
          <li><strong>Temperatures Analyzed:  </strong><xsl:value-of select="test/user-inputs/temperatures-analyzed"/></li>
          <li><strong>Temperature Tolerance:  </strong><xsl:value-of select="test/user-inputs/temperature-tolerance"/>°C</li>
          <li><strong>Voltage Tolerance:  </strong><xsl:value-of select="test/user-inputs/voltage-tolerance"/>V</li>
        </ul>
        <br/>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>