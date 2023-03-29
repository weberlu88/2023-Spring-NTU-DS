#ifndef RPCS_H
#define RPCS_H

#include "chord.h"
#include "rpc/client.h"

#include <iostream>
#include <vector>
#include <cstdint>


Node self, successor, predecessor;
static int finger_size = 4; // finger table store 4 entries
std::vector<Node> finger_table(finger_size);
std::vector<Node> successor_list(3);

Node get_info() { return self; } // Do not modify this line.
Node get_predecessor() { return predecessor; }
Node get_successor() { return successor; } // for python testing
std::vector<Node> get_successor_list() { return successor_list; }
void fix_dead_successor();
void fix_dead_candidate();
// ====== start of the utility functions ======

/**
 * add 2 id. range = [0, 2^32-1] 共2^32個id, ps: 2^32-1 = 4294967295
*/
uint64_t add_id(uint64_t id1, uint64_t id2) {
  return (id1 + id2) & ((1UL << 32) - 1); // mod 2^32-1
}

/** id is in (a, b), conserning cicurlar ring. */
bool isBetween(uint64_t id, uint64_t a, uint64_t b){
  if (b > a) {
    // true:  3 in (1, 5)
    // false: 3 not in (4, 5)
    return (id > a && id < b); 
  } else { // b <= a
    // true: 3 in (31, 5) ps跨過0了
    // false 3 not in (31, 1)
    return ( id > a || id < b);
  }
}

/** id is in (a, b], conserning cicurlar ring. */
bool isBetween_inclusive(uint64_t id, uint64_t a, uint64_t b){
  if (b > a) {
    // true: 3 in (1, 3) also in (1, 5)
    return (id > a && id <= b);
  } else { // b <= a
    // true: 3 in (31, 3) also in (31, 5)
    return ( id > a || id <= b);
  }
}

// ====== start of the program functions ======
// todo: 寫一個 function to get finger's id 讓最後一個 finger 繞半圈

/** Used in stablize()*/
void change_predecessor(Node n) {
  predecessor = n;
}

// void change_successor(Node n) {
//   successor = n;
// }

void create() {
  predecessor.ip = "";
  successor = self;
  successor_list[0] = self;
}

/**
 * Join ring containing Node n.
*/
void join(Node n) {
  predecessor.ip = "";

  try {
    rpc::client client(n.ip, n.port); // get the known node instance
    successor = client.call("find_successor", self.id).as<Node>(); // ask who is my successor, giving my id as param
    
    std::vector<Node> new_s_lst = client.call("get_successor_list").as<std::vector<Node>>();

    successor_list[0] = successor;
    successor_list[1] = new_s_lst[0];
    successor_list[2] = new_s_lst[1];

    // std::cout << "join: Node " << self.id << "\n";
    // std::cout << "  Slist 0:" << new_s_lst[0].id  << std::endl;
    // std::cout << "  Slist 1:" << new_s_lst[1].id  << std::endl;
    // std::cout << "  Slist 2:" << new_s_lst[2].id  << std::endl;
  } catch (std::exception &e) {
    // std::cout << "join: error" << std::endl;
  }
}

/**
 * Used by find_successor().
 * search for for the highest predecessor of id.
 * 從 finger table 中由後往回，尋找 finger in (我, keyid)的finger，如果沒finger便自己負責
 * ex: i'm n8, keyid=54 (n48 in (n8, k54)), return finger n48
*/
Node closest_preceding_node (uint64_t id) {
  for ( int i = finger_size-1; i >= 0; i-- ){
    // test print
    // if (self.id == 373792412 && id == 100663296) { // 373792412 is port 5059
    //   std::cout << "ID:" << id << "\n";
    //   std::cout << "Finger id:" << finger_table[i].id << "\n";
    //   std::cout << "Self id:" << self.id << "\n";
    // }    

    // 一個 node 負責的 range 為 [pre_id+1, node_id] == (pre_id, node_id]
    // node_id 不重複，所以 == (pre_id, node_id) ??
    if ( isBetween(finger_table[i].id, self.id, id) ){
      if (finger_table[i].id != self.id && finger_table[i].id != 0){
        return finger_table[i];
      }
    }
  }

  // 當沒有 successor 時，才會由我負責
  return self;
}

/**
 * Find successor given keyid. Successor 負責的範圍是 (n-1, n] 但不考慮id重複
*/
Node find_successor(uint64_t id) {
  Node closest_node;
  try {

    // 繼任者負責這個 id -> return 繼任者
    if ( isBetween_inclusive(id, self.id, successor.id) ){
      return successor;
    } else {
      // 剩下的選項只剩我自己，和 finger 中的 node
      closest_node = closest_preceding_node(id);
      if (closest_node.id == self.id){
        // 我負責
        return self;
      } else {
        // 由某個 finger 負責、或最後一個 finger 繼續找下去
        rpc::client client(closest_node.ip, closest_node.port); 
        return client.call("find_successor", id).as<Node>();
      }
    }

  } catch (std::exception &e) {
    // std::cout << "Node:" << self.id << " find_successor error" << "\n" ;
    // std::cout << "  closest_node: " << closest_node.id << "\n" ;
  }
  return self;
}

/**
 * Called periodicly
 * predecessor: Ring 中的前任者，即指向我的 Node
 * 若 predecessor 離線將 ip 設為空字串
*/
void check_predecessor() {
  try {
    rpc::client p(predecessor.ip, predecessor.port);
    Node n = p.call("get_info").as<Node>();
  } catch (std::exception &e) {
    predecessor.ip = "";
    // std::cout << "check_predecessor: error \n";
  }
}

uint64_t next = 0; // index to refresh
/**
 * Called periodicly
 * Refresh finger table entry, refresh one entry at one call.
*/
void fix_fingers(){
  try {
    if (next >= (uint64_t)finger_size){
      next = 0;
    }

    if (next == 0){
      finger_table[next] = successor;
    } else {
      finger_table[next] = find_successor(add_id(self.id, (1ULL << (28+next)) ));
    }

    // std::cout << "fix_fingers: Node " << self.id << "\n";
    // std::cout << "  Finger " << next << " ID:" << add_id(self.id, (1ULL << (28+next)) ) << "\n";
    // std::cout << "  Finger " << next << " Node:" << finger_table[next].id << "\n";
    
    next++;
  } catch (std::exception &e) {
    // std::cout << "fix_fingers error" << "\n" ;
  } 
}

/**
 * Used in stablize()
 * successor_list stores 5 fingers, replace a new node on a old node.
 * @param died_node old node object to be replaced.
 * @param new_node new node object.
 */
void update_finger_table(Node died_node, Node new_node){
  for (int i=0; i<=finger_size-1; i++){
    if (finger_table[i].id == died_node.id) {
      finger_table[i] = new_node;
    }
  }
}

/**
 * Used in stablize()
 * successor_list stores the next 3 successor, make a direct update on 1st.
 * call 1st get_successor_list() to update the 2nd, 3nd one.
 */
void update_successor_list(Node first_successor) {
  successor_list[0] = first_successor;

  rpc::client client(successor.ip, successor.port); 
  std::vector<Node> new_successor_list = client.call("get_successor_list").as<std::vector<Node>>();

  successor_list[1] = new_successor_list[0];
  successor_list[2] = new_successor_list[1];

}

/**
 * Only one node in the ring.
*/
void initiate_ring(){
  for (auto n: finger_table){
    n = self;
  }
  for (auto n: successor_list){
    n = self;
  }

  successor = self;
  predecessor = Node{};
}

/**
 * stabilize() 檢查我和繼任者中間是否被插隊，有則換掉我的繼任者為n'，並通知繼任者n'。
 * notify(n') 修正我的前任，此方法由別人喚醒。
 * ex: N21 檢查自己和 N32 之間，被 N24 插入，new 繼任者 is N24。
*/
void stablize(){
  
  Node candidate_s;

  if ( successor.id != 0 && self.id != successor.id ) {
    // Get successor's predecessor
    // case 1: successor's predecessor is myself
    // case 2: successor's predecessor is a new inserted node
    try {
      rpc::client client(successor.ip, successor.port); 
      candidate_s = client.call("get_predecessor").as<Node>();
    } catch (std::exception &e) {
      fix_dead_successor(); // handle if successor failed
    }

  } else { 
    // When i'm the root node [self.id == successor.id]
    candidate_s = predecessor;
  }

  // if candidate_s exist, check weather to change the successor to candidate_s (case 2)
  // then notify candidate_s i'm possible your predecessor
  if (candidate_s.id != 0) { 
    if ( isBetween(candidate_s.id, self.id, successor.id) ) {
      successor = candidate_s;
      // std::cout << "stablize: change successor id:" << successor.id << "\n";
    } 
  } 
  
  if ( successor.id != 0 && self.id != successor.id) {
    try {
      rpc::client client(successor.ip, successor.port);
      client.call("notify", self);   
    } catch (std::exception &e) {
      fix_dead_candidate(); // handle if candidate failed to notify
    }
    
    try {
      update_successor_list(successor);
    } catch (std::exception &e) {
      fix_dead_successor(); // handle if successor failed
    }
  }
}

/**
 * Used in stablize().
 * Notifier think he is my predecessor，若 notifier 插隊在我和目前的 predecessor 之間，將 notifier 改成新的 predecessor。
 * 需由其他 Node 呼叫，不能由自己呼叫
*/
void notify(Node notifier){
  if ( predecessor.ip == "" || isBetween(notifier.id, predecessor.id, self.id) ) {
    predecessor = notifier;
    std::cout <<"notify: "<<self.id<<" recieve from "<<predecessor.id<<", predecessor changed\n" ;
  }
}

/**
 * Used in stablize().
 * Handle after changing the successor to successor.predecessor, successor.predecessor failed.
 * Approach: restore the origin successor from successor_list[0].
*/
void fix_dead_candidate() {
  successor = successor_list[0];
  rpc::client client(successor.ip, successor.port);
  try {
    client.call("change_predecessor", Node{});
  } catch (std::exception &e) {
    // do nothing
  }
}

/**
 * Used in stablize().
 * Handle if the first node (both first two nodes) of successor_list failed. (invoked by exception during rpc call)
 * Finger table: replace the dead finger(s) with a alive successor.
 * Successor & Successor_list: replace the dead successor(s) with a alive successor.
*/
void fix_dead_successor() {
  rpc::client* client;
  try
  {
    // the first node of successor_list failed
    if (successor_list[1].id != self.id)
    {
      client = new rpc::client(successor_list[1].ip, successor_list[1].port);
      std::vector<Node> new_successor_list = client->call("get_successor_list").as<std::vector<Node>>();

      /*update successor, successor_list, finger_table*/
      update_finger_table(successor_list[0], successor_list[1]);

      successor = successor_list[1];
      successor_list[0] = successor_list[1];
      successor_list[1] = new_successor_list[0];
      successor_list[2] = new_successor_list[1];
    }
    else
    {
      // successor == self, so only exit one node
      initiate_ring();
    }
  }
  catch (std::exception &e)
  {
    // the first two node of successor_list failed
    try
    {
      if (successor_list[1].id != self.id)
      {
        client = new rpc::client(successor_list[2].ip, successor_list[2].port);
        std::vector<Node> new_successor_list = client->call("get_successor_list").as<std::vector<Node>>();

        update_finger_table(successor_list[0], successor_list[2]);
        update_finger_table(successor_list[1], successor_list[2]);

        successor = successor_list[2];
        successor_list[0] = successor_list[2];
        successor_list[1] = new_successor_list[0];
        successor_list[2] = new_successor_list[1];
      }
      else
      {
        // successor == self, so only exit one node
        initiate_ring();
      }
    }
    catch (std::exception &e)
    {
      // do nothing
      // successor_list[1] still dead, can find successor_list[2] as alt, but i'm lazy.
    }
  }
}


/**
 * Binding "name" to function on sever which exposed to rpc call
*/
void register_rpcs() {
  add_rpc("get_info", &get_info); // Do not modify this line.

  add_rpc("create", &create);
  add_rpc("join", &join);
  add_rpc("get_predecessor", &get_predecessor); 
  add_rpc("change_predecessor", &change_predecessor);
  add_rpc("get_successor", &get_successor);
  add_rpc("get_successor_list", &get_successor_list);
  add_rpc("find_successor", &find_successor);
  add_rpc("notify", &notify);
}

/**
 * Invoked periodically (every 2s)
*/
void register_periodics() {
  // 順序不建議調換
  add_periodic(check_predecessor);
  add_periodic(stablize);
  add_periodic(fix_fingers);
}

#endif /* RPCS_H */
