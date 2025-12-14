# Helper script to generate .lss file with splits for all levels.

if __name__ == '__main__':
    sections = []
    
    sections.append("""<?xml version="1.0" encoding="UTF-8"?>
<Run version="1.7.0">
  <GameIcon />
  <GameName>Ambidextro</GameName>
  <CategoryName>Any%</CategoryName>
  <LayoutPath>
  </LayoutPath>
  <Metadata>
    <Run id="" />
    <Platform usesEmulator="False">
    </Platform>
    <Region>
    </Region>
    <Variables />
    <CustomVariables />
  </Metadata>
  <Offset>00:00:00</Offset>
  <AttemptCount>0</AttemptCount>
  <AttemptHistory />
  <Segments>""")
    
    for level in range(0, 102):
        sections.append(f"""
    <Segment>
      <Name>Level {level:03d}</Name>
      <Icon />
      <SplitTimes>
        <SplitTime name="Personal Best" />
      </SplitTimes>
      <BestSegmentTime />
      <SegmentHistory />
    </Segment>""")
    
    sections.append("""
  </Segments>
  <AutoSplitterSettings />
</Run>""")
    
    with open('Ambidextro - Any%.lss', mode='w', encoding='utf8') as f:
        f.write(''.join(sections))
    
    print("Written splits to 'Ambidextro - Any%.lss'")