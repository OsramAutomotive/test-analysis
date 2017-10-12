<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">

  <html>
    <head>
      <!-- <meta http-equiv="refresh" content="15"></meta> -->
      <meta http-equiv="pragma" content="no-cache"></meta>
      <link rel="stylesheet" type="text/css" href="styles.css"></link>
      <!-- <script>setTimeout('window.location.reload();', 5000);</script> -->
    </head>

    <body>
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

      <!-- Temperature Header -->
      <xsl:for-each select="test/temperature">
        <h2><div contenteditable="true"><xsl:value-of select="@temp"/></div></h2>
    
        <xsl:for-each select="mode">

          <table border="1">
            <!-- Mode Header -->
            <tr>
              <xsl:attribute name="class"><xsl:value-of select="@id"/></xsl:attribute>
              <th>
                <xsl:attribute name="colspan"><xsl:value-of select="@width"/></xsl:attribute>
                <div contenteditable="true"><xsl:value-of select="@id"/></div>
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
                    <xsl:otherwise>
                      <td align="center"><xsl:value-of select="check"/></td>
                    </xsl:otherwise>
                  </xsl:choose>
                </xsl:for-each>
              </tr>

            </xsl:for-each>
          </table>
          <br/><br/>

        </xsl:for-each><!-- end mode -->
        <br/><br/><br/>
      </xsl:for-each><!-- end temperature -->


      <h2>User Inputs</h2>
      <ul>
        <li><strong>Test Name:  </strong><xsl:value-of select="test/user-inputs/test-name"/></li>
        <li><strong>Data Folder:  </strong><xsl:value-of select="test/user-inputs/folder"/></li>
        <li><strong>DUTs:  </strong><xsl:value-of select="test/user-inputs/systems"/></li>
        <li><strong>Limits File:  </strong><xsl:value-of select="test/user-inputs/limits-file"/></li>
        <li><strong>Temperature Tolerance:  </strong><xsl:value-of select="test/user-inputs/temperature-tolerance"/>°C</li>
        <li><strong>Voltage Tolerance:  </strong><xsl:value-of select="test/user-inputs/voltage-tolerance"/>V</li>
      </ul>

      <br/>

    </body>
  </html>

</xsl:template>
</xsl:stylesheet>